from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from resources.tag_categories import KAOMOJI, COLOR_DICT

from resources import parameters
from classes.class_database import Database
from interfaces import statistics

import datetime
import pandas as pd
import os
from collections import Counter
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from clip import tokenize

# clustering text --> groups, not encoding to latent space for few reasons
#from sklearn.cluster import HDBSCAN
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.metrics.pairwise import pairwise_distances

# code to check tokens
"""
from resources import tag_categories
tag_list = list(set(list(parameters.DESCRIPTION_TAGS_FREQUENCY.keys())+list(tag_categories.COLOR_DICT.keys())))
known_text = tokenize(tag_list, context_length=77)
token_dict = {}
for tag, tokens in zip(tag_list, known_text):
    token_dict[tag] = [int(tk) for tk in tokens[tokens.nonzero()[1:-1]]]

        

alphabet = list(map(chr, range(97, 123)))
mod_check = [alp*i for alp in alphabet for i in range(6, 10)]
mod_check_add = [alp*3 + alpx*3 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*2 + alpx*3 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*3 + alpx*2 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*2 + alpx*2 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*4 + alpx*3 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*3 + alpx*4 for alp in alphabet for alpx in alphabet if alp!=alpx]
mod_check_add += [alp*4 + alpx*4 for alp in alphabet for alpx in alphabet if alp!=alpx]
parameters.log.info(mod_check_add)
mod_check+=mod_check

artist_pot = ["artist" + mod for mod in mod_check]
#code here
known_text = tokenize(artist_pot, context_length=77)
for tag, tokens in zip(artist_pot, known_text):
    token = [int(tk) for tk in tokens[tokens.nonzero()[1:-1]]]
    if len(token) == 2 and token[0] == 14326:
        printv = True
        for k, v in token_dict.items():
            if any([tc in v for tc in token[1:]]):
                printv = False
                break
        if printv:
            parameters.log.info(tag)
"""       

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig_obj = Figure(figsize=(width, height), dpi=dpi, facecolor="#BFBFBF", tight_layout=True)
        self.axes = self.fig_obj.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig_obj)

class TokenView(QtCore.QAbstractListModel):
    def __init__(self, token_info, color_dict, parent=None):
        """
        :param token_info: list of ("token", token breakdown, token overlap count) pairs
        """
        super().__init__(parent)
        self.token_info = token_info
        self.counter_len = len(self.token_info)
        self.color_dict = color_dict
    
    def rowCount(self, parent):
        return self.counter_len
    
    def data(self, index, role):
        token_line = self.token_info[index.row()]
        if role == QtGui.Qt.ItemDataRole.DisplayRole:
            if len(token_line) > 1:
                return str(token_line[0]) + ", " + str(token_line[1])
            else:
                return str(token_line[0])
            
        if role == QtGui.Qt.ItemDataRole.ForegroundRole:
            # return a preselected color for a tag or return the default color
            brush = QtGui.QBrush()
            tag_val = str(token_line[0])
        
            if tag_val in self.color_dict:
                (red, green, blue, alpha) = self.color_dict[tag_val]
                brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
            else:
                # default black
                brush.setColor(QtGui.QColor.fromRgb(255,255,255,255))
            return brush
        
class StatisticsView(QWidget, statistics.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        
        self.df = None # (sparse) panda dataframe
        self.fig = None
        self.folder_name = ""
        self.tag_counter = Counter()
        self.graph_generated = False
        self.pushButton_load_database.clicked.connect(self.load_database_button)
        self.pushButton.clicked.connect(self.generate_graph_button)
        #self.pushButton_2.clicked.connect(self.save_graph_button) # disabled because matplotlib has a save button
        self.pushButton_threshold_view.clicked.connect(self.threshold_view_button)
        self.pushButton_quality.clicked.connect(self.quality_check)
        self.lineEdit_token_input.returnPressed.connect(self.update_token_info)

    @Slot()
    def load_database_button(self):
        folder = self.lineEdit_folder.text()
        if folder:
            parameters.log.info(("Loading dataset", str(folder)))
            self.folder_name = os.path.basename(folder)
            parameters.log.info((self.folder_name, "foldername"))
            self.temp_database = Database(folder)
            parameters.log.info(f"Loaded database with {len(self.temp_database.images)} imgs")

    @Slot()
    def generate_graph_button(self):
        proceed = True
        if len(self.temp_database.images) > 5000:
            parameters.log.info("This process may be costly, you have over 5k image data loading.")
            ans = input("Proceed? (Y/n)")
            ans = str(ans).lower()
            if ans != "y":
                proceed = False
        if proceed:
            self.generate_statistics()
            top_tags = self.generate_df()
            #self.generate_HDBSCAN(top_tags)
            self.generate_graph()

    @Slot()
    def generate_graph(self):
        # run the statistic first, this also sets tag_counter
        
        hw_size = int(self.lineEdit.text())
        if hw_size < 0:
            hw_size = 100
            parameters.log.warn("Detected invalid value, defaulting to max 100")
        hw_size = min(self.df.shape[0], hw_size)
        parameters.log.info(f"Generating graph using {hw_size} for height and width")
        top_tags = []
        top_tag_count = []
        for k, v in self.tag_counter.most_common(hw_size):
            top_tags.append(k)
            top_tag_count.append(v)
        df = self.df.loc[top_tags,top_tags]
       
        line_width = 5
        xy_axis = [k + " (" + str(v) +")" for k, v in zip(top_tags, top_tag_count)]
        sc = MplCanvas(self, 40, 20)
        #plt.figure(figsize=(40,40))
        heatmap_fig = sns.heatmap(df, ax=sc.axes, annot=False, xticklabels=xy_axis, yticklabels=xy_axis, square=True, cbar_kws={'shrink': 0.8})
        
        heatmap_fig.hlines([i*line_width for i in range(int(hw_size/line_width))], *heatmap_fig.get_xlim())
        heatmap_fig.vlines([i*line_width for i in range(int(hw_size/line_width))], *heatmap_fig.get_ylim())
        sc.axes.set_title(self.folder_name+": Frequency Heatmap", fontsize=25)
        sc.axes.set_xticks(sc.axes.get_xticks(), sc.axes.get_xticklabels(), rotation=-60, ha='left')
        #plt.subplots_adjust(left=0, right=0.9, top=0.95, bottom=0.23, wspace=0.2, hspace=0.2)
        #sc.fig_obj.tight_layout()
        self.fig = heatmap_fig.get_figure()
        
        self.navi_toolbar = NavigationToolbar(sc, self)
        while self.gridLayout_4_graph.takeAt(0) is not None:
            child = self.gridLayout_4_graph.takeAt(0)
            widget = child.widget()
            del widget # del the widget
            del child  # del the layout item
        self.gridLayout_4_graph.addWidget(sc)
        self.gridLayout_4_graph.addWidget(self.navi_toolbar)
        parameters.log.info("Finished graph")

    def generate_df(self):
        # generates the df used for the graph and return the top tags used for HDBSCAN
        min_threshold = 10 if len(self.temp_database.images) > 100 else 1
        top_tags = [k for (k, v) in self.tag_counter.most_common() if v >= min_threshold]
        top_tags_set = set(top_tags)
        tag_len = len(top_tags)
        self.df = pd.DataFrame({val: [0 for _ in range(tag_len)] for val in top_tags}, index=top_tags,columns=top_tags)

        # add a row filled with 1 or 0 if the matching tags are in a file
        for img in self.temp_database.images:
            tags = [t for t in img.get_full_tags() if t in top_tags_set]
            for t in tags:
                self.df.loc[t,tags] +=1

        # fill the upper triangle with zeros
        for i, t in enumerate(top_tags):
            if i != tag_len-1:
                self.df.loc[t, top_tags[i+1:]] = 0

        # divide the row by the largest value
        for k, v in self.tag_counter.most_common(tag_len):
            self.df[[k]] = self.df[[k]]/v
        
        return top_tags

    def generate_HDBSCAN(self, top_tags):
        vocab = top_tags
        # we override the preprocessor and tokenizer because we already have the sequence separated into a list
        #vectorizer = CountVectorizer(vocabulary=vocab, tokenizer=lambda x: x, preprocessor=lambda x: x, lowercase=False, stop_words=None)
        hdbs = HDBSCAN(min_cluster_size = 5, alpha=1.0, algorithm="auto", n_jobs=-1, 
                       cluster_selection_method="eom", allow_single_cluster=False)#metric='precomputed'
        
        corpus = [[t for t in img.get_full_tags() if t in vocab] for img in self.temp_database.images]
    
        #X = [vectorizer.transform(tags) for tags in corpus]
        X = [[1 if v in full_tags else 0 for v in vocab] for full_tags in corpus]
        # Calculate pairwise cosine distances
        #pairwise_distances_cosine = pairwise_distances(X, metric='cosine')
          
        #("tfid", TfidfTransformer())
         # 2D array [[0,1,0,0,....], ...] <- list of vectorized tags
        # basic assumptions about the data:
        # 1.) the data is not noise or one blob of data, there's smaller meaningful subsets in the data
        # 2.) since this is textual data, cosine is more relavant than euclidian distance
        # 3.) we assume there's some ammount of data, so min cluster is set to 10
        #labels = hdbs.fit_predict(pairwise_distances_cosine)
        labels = hdbs.fit_predict(X)
        # class labels are non-negative integers, negative labels are noise/missing/inf elements.
        max_classes = max(labels)
        parameters.log.info(f"Finished labeling clusters, found {max_classes+1} classes")
        parameters.log.info((labels, len(labels)))
        parameters.log.info(f"{sum([i > -1 for i in labels])} were placed in a group and {sum([i < 0 for i in labels])} were classified as noise")
        
        # -1 for noise, the rest is the classes
        counter_list = [Counter() for _ in range(max_classes+2)]
        counter_size = [0 for _ in range(max_classes+2)]
        for i, clss in enumerate(labels):
            counter_list[clss].update(corpus[i])
            counter_size[clss]+=1
        
        classes = [i for i in range(-1, max_classes+1)]
        counter_features = [list(cf.most_common()) for cf in counter_list]
        temp_df = pd.DataFrame({c: [0 for _ in classes] for c in vocab}, index=classes,columns=vocab, dtype=float)
        parameters.log.debug(temp_df.head())
        for class_index in classes:
            for cf in counter_features[class_index]:
                temp_df.loc[class_index,cf[0]] = float(cf[1]/counter_size[class_index])
        parameters.log.info(temp_df.head())
        filter_col = []
        for tag in top_tags:
            if (temp_df[tag] > 0.7).all() and (temp_df[tag] > 0.3).any():
                filter_col.append(tag)
        parameters.log.info(("Filter", filter_col))
        parameters.log.info(temp_df.drop(columns=filter_col))
        
        parameters.log.info("Fin")
        
    @Slot()
    def generate_statistics(self):
        """
        loop all the images, get the tag length, tag conflicts, and display the summary statistics
        """
        tag_len = []
        tag_conflict_len = []
        self.tag_counter = Counter()
        self.rejected_counter = Counter()
        self.tag_conflict_counter = Counter()
        for img in self.temp_database.images:
            tags = img.get_full_tags()
            rejected_tags = img.get_rejected_tags()
            tag_conflict_categ = img.get_unresolved_conflicts()
            tag_conflict_len.append(len(tag_conflict_categ))
            self.tag_counter.update(tags)
            self.rejected_counter.update(rejected_tags)
            self.tag_conflict_counter.update(list(tag_conflict_categ.keys()))
            tag_len.append(len(tags))
        tag_series = pd.Series(tag_len)
        tag_conflict_series = pd.Series(tag_conflict_len)
        unique_rejected = len(self.rejected_counter)
        unique_tags = len(self.tag_counter)
        parameters.log.info("Tag conflicts occurance per category")
        parameters.log.info([(c, v) for c, v in self.tag_conflict_counter.most_common()])
        #tag_description = tag_series.describe().apply("{0:.2f}".format)
        conflict_description = tag_conflict_series.describe(exclude=['count']).loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']].round(2)

        self.label_5.setText(f"Unique Tags Post Filter: {unique_tags}\nUnique Rejected Tags: {unique_rejected}\n\nUsed Tags:\n{tag_series.describe().round(2)}\n\nTag Conflict Categories:\n{conflict_description}")

    @Slot()
    def save_graph_button(self):
        if self.fig:
            parameters.log.info("Saving graph")
            ct = datetime.datetime.now()
            ct = [str(tm) for tm in [ct.year, ct.month, ct.day, ct.hour, ct.minute]]
            filename = "heatmap_"+self.folder_name+"_"+ct[0]+"_"+ct[1]+"m"+ct[2]+"d_EST"+ct[4]+"_"+ct[4]+"min.png"
            heatmap_folder = os.path.join((parameters.MAIN_FOLDER, "heatmaps"))
            self.fig.savefig(os.path.join(heatmap_folder, filename), bbox_inches='tight', pad_inches=0.1)
        else:
            parameters.log.info("No figure to save")

    @Slot()
    def threshold_view_button(self):
        lower_bound=float(self.lineEdit_lower_bound.text())
        upper_bound=float(self.lineEdit_higher_bound.text())
        if lower_bound < upper_bound:
            if lower_bound < 0:
                parameters.log.info("Technically legal, but lower bound should be >= 0")
            elif upper_bound > 1:
                parameters.log.info("Technically legal, but upper bound should be <= 1")
            len_counter = []
            tag_counter = Counter()
            for img in self.temp_database.images:
                tags = [t[0] for t in img.auto_tags if lower_bound <= t[1] <= upper_bound]
                len_counter.append(len(tags))
                tag_counter.update(tags)
            len_series = pd.Series(len_counter)
            unique_tag_count = len(tag_counter)
            tag_freq_list = list(tag_counter.most_common())
            if max(len_counter):
                parameters.log.info(f"Printing tags between {lower_bound} and {upper_bound}")
                parameters.log.info(tag_freq_list)
                parameters.log.info(f"There was a total {unique_tag_count} unique tags")
                parameters.log.info("Breakdown of # of tags within the threshold for each entry")
                parameters.log.info(len_series.describe())
            else:
                parameters.log.info(f"No tags between {lower_bound} and {upper_bound}")
        else:
            parameters.log.info("Lower threshold must be smaller than upper threshold, probability between 0~1")
        
    def quality_check(self):
        if self.temp_database:
            labels = [img.score_label for img in self.temp_database.images]
            scores = [img.score_value for img in self.temp_database.images]
            
            if len([l for l in labels if l]) > 0:
                score_labels = Counter(labels)
                ds_size = len(scores)
                scores_series = pd.Series(scores)

                scores_df = pd.DataFrame.from_dict({"Scores":scores, "Labels":labels})
                
                
                while self.gridLayout_4_graph.takeAt(0) is not None:
                    child = self.gridLayout_4_graph.takeAt(0)
                    widget = child.widget()
                    del widget # del the widget
                    del child  # del the layout item
                
                from resources.tag_categories import QUALITY_LABELS
                
                sc = MplCanvas(self, 40, 20)
                if max(scores) > 1: # have this for compatibility with old database
                    bin_size = 60
                    bin_range = (0, 6)
                else:
                    bin_size = 50
                    bin_range = (0, 1)
                
                hist_fig = sns.histplot(data=scores_df,x="Scores", bins = bin_size, binrange=bin_range, ax=sc.axes, hue="Labels", hue_order=QUALITY_LABELS)
                sc.axes.set_title(self.folder_name+": Quality score distribution", fontsize=25)
                self.fig = hist_fig.get_figure()
                self.gridLayout_4_graph.addWidget(sc)
                
                
                result = "\n".join([f"{f:<10}: {score_labels[f]:<6} ({(score_labels[f]/ds_size)*100:.2f}%)" for f in QUALITY_LABELS])
                
                self.label_5.setText(f"Aesthetics Score Statistics:\nDistribution Statistic:\n{scores_series.describe().round(2)}\n\nCounter for Each Category:\n{result}")
            else:
               parameters.log.error("No score and score label in database, no graph to generate")        
            
        else:
            parameters.log.error("No database loaded")
                
    @Slot()
    def update_token_info(self):
        """_summary_
        reads the text, convert to tokens, then write other tags with overlapping tokens
        """
        text = self.lineEdit_token_input.text()
        text = text.strip()
        if text:
            if not hasattr(self, "token_dict"):
                parameters.log.info("One time token evaluation for known tags")
                from tools import files
                ca_dict = files.get_dict_caformer_tag_frequency()
                swin_df = files.get_pd_swinbooru_tag_frequency()
                
                
                
                tag_list = list(set(swin_df["name"].tolist()+list(ca_dict.values()) + list(COLOR_DICT.keys())))
                
                # process tags
                
                tag_list = [t.replace("_", " ") if len(t) > 3 and t not in KAOMOJI else t for t in tag_list]
                print(tag_list[:10])
                known_text = tokenize(tag_list, context_length=500)
                self.token_dict = {}
                for tag, tokens in zip(tag_list, known_text):
                    self.token_dict[tag] = [int(tk) for tk in tokens[tokens.nonzero()[1:-1]]]
                    
                
            text_token = tokenize(text, context_length=500)[0]
            
            text_token = [int(tk) for tk in text_token[text_token.nonzero()[1:-1]]]
            
            self.label_token_count.setText(f"Token count: {len(text_token)}, Tokens: {text_token}")
            
            write_pair = []
            for k, v in self.token_dict.items():
                if any([tc in v for tc in text_token]):
                    write_pair.append((k, v, sum([tc in v for tc in text_token])))
              
            if write_pair:
                # sort write pair, - is for ascending order
                write_pair = sorted(write_pair, key=lambda x: (-x[2], x[0]))
                self.listView_tokens.setModel(TokenView(write_pair, COLOR_DICT))
            else:
                self.listView_tokens.setModel(TokenView([["No directly related Tokens/Tags"]], {}))    
        else:
            self.label_token_count.setText(f"Token count:")
            self.listView_tokens.setModel(None)
        