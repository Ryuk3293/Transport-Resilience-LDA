# -*- coding: utf-8 -*-
"""country_region mapping.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Lshfk6edSAjKQnizlCioVwi86DzN4JBd
"""

pip install pdfminer

pip install pyLDAvis

pip install dash_bio

pip install pycountry

# Commented out IPython magic to ensure Python compatibility.
import re
import numpy as np
import pandas as pd
from pprint import pprint
# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
# spacy for lemmatization
import spacy
# Plotting tools
import pyLDAvis
import pyLDAvis.gensim_models  # don't skip this
import matplotlib.pyplot as plt
# %matplotlib inline
# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
# NLTK Stop words
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'slr', 'index', 'nile'])

import sys
# sys.setdefaultencoding("utf-8")
import imp
imp.reload(sys)
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage
from pdfminer.converter import PDFPageAggregator
import re
import os
import pycountry
from collections import Counter

from google.colab import drive
drive.mount('/content/drive')

path = "/content/drive/MyDrive/Papers"
files= os.listdir(path)
list_text = []
for file in files:
    if not os.path.isdir(file):
        fp = open(path+"/"+file,'rb')
        parser = PDFParser(fp)
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        document = PDFDocument(parser)
        text_content = []
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    text_content.append(lt_obj.get_text())
                else:
                    pass
        total_text = ''.join(text_content).replace("\n"," ")
        list_text.append(total_text)
len(list_text)

# Get a set of all country names
countries_set = set()
for country in pycountry.countries:
    countries_set.add(country.name)
    if hasattr(country, "official_name"):
        countries_set.add(country.official_name)

# Load spaCy English model
origin_country = []
nlp = spacy.load("en_core_web_sm")

# Process text and extract entities
def extract_entities(text):
    doc = nlp(text)
    countries = [ent.text for ent in doc.ents if ent.label_ == "GPE" and ent.text in countries_set]  # Filter for geopolitical entities
    country_freq = Counter(countries)
    return countries, country_freq




# Extract entities from the text
for i in list_text:
  countries, freq = extract_entities(i)
  if not freq:
      print("No country found in the text.")
      origin_country.append('NA')
  else:
      # Get countries with the highest frequencies
      most_common_countries = freq.most_common(1)  # Change 3 to the desired number of countries to retrieve
      print("Countries with the highest frequencies:", most_common_countries)
      origin_country.append((most_common_countries[0][0]))

count_na = 0
for i in origin_country:
  if i == 'NA':
    origin_country.remove(i)
    count_na+=1
print('docs with no country info ', count_na)

Unq_Country = []
for i in origin_country:
  if i not in Unq_Country:
    Unq_Country.append(i)
print(len(Unq_Country))

import matplotlib.pyplot as plt
from collections import Counter

# Example list
my_list = origin_country

# Use Counter to count the occurrences of each item
item_counts = Counter(my_list)

# Remove items with count 1
item_counts = {item: count for item, count in item_counts.items() if count > 1}

# Extract items and counts for plotting
items = list(item_counts.keys())
counts = list(item_counts.values())

# Plotting the bar chart
plt.figure(figsize=(12, 6))  # Increase the width of the figure
plt.bar(items, counts, color='skyblue')

# Adding labels and title
plt.xlabel('Countries')
plt.ylabel('Count')
plt.title('Count of publications')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')  # Rotate labels to 45 degrees and align to the right

# Display the plot
plt.tight_layout()  # Adjust layout to prevent clipping
plt.show()



item_counts

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

# Define functions for stopwords, bigrams, trigrams and lemmatization
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

data_words = list(sent_to_words(list_text))
# Build the bigram and trigram models
bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

# See trigram example
print(trigram_mod[bigram_mod[data_words[0]]])

# Remove Stop Words
data_words_nostops = remove_stopwords(data_words)

# Form Bigrams
data_words_bigrams = make_bigrams(data_words_nostops)

# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
# python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

# Do lemmatization keeping only noun, adj, vb, adv
data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

print(data_lemmatized[:1])

# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized)
# Create Corpus
texts = data_lemmatized
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]
# View
# print(corpus)



# Build LDA model # SP changed value of K from 20 to others
K_best = 1
CS_max = 0
for K in range(0,25):
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=K+1,
                                               random_state=100,
                                               update_every=1,
                                               chunksize=50,
                                               passes=20,
                                               alpha='auto',
                                               per_word_topics=True)
    # Compute Perplexity
    print('K=',K+1)
    print('Perplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.

    # Compute Coherence Score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='c_v')

    coherence_lda = coherence_model_lda.get_coherence()
    print('Coherence Score: ', coherence_lda)

    if coherence_lda > CS_max:
        K_best = K+1
        CS_max = coherence_lda
print(K_best, CS_max)

# Build best LDA model
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics= K_best,
                                           random_state=100,
                                           update_every=1,
                                           chunksize=50,
                                           passes=20,
                                           alpha='auto',
                                           per_word_topics=True)
# Visualize the topics
import pyLDAvis.gensim_models
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
vis



# Assuming you have two lists: corpus (containing n documents) and countries (containing corresponding country for each document)
# Assuming corpus and countries are lists of equal length

corpus_by_country = {}

for doc, country in zip(corpus, origin_country):
    if country not in corpus_by_country:
        corpus_by_country[country] = []
    corpus_by_country[country].append(doc)

# for i, subset1 in enumerate(corpus_by_country):
#   print(i)
#   print('sub is')
#   print(subset1)

from gensim.matutils import hellinger
from scipy.spatial.distance import jensenshannon

# Define two subsets of documents
corpus_subset1 = corpus_by_country['China']
corpus_subset2 = corpus_by_country['Sweden']

# Get topic distributions for each subset
topic_distributions1 = [lda_model.get_document_topics(doc, minimum_probability=0) for doc in corpus_subset1]
topic_distributions2 = [lda_model.get_document_topics(doc, minimum_probability=0) for doc in corpus_subset2]

# Calculate Hellinger distance or Jensen-Shannon divergence for each pair of documents
for i, (doc1, doc2) in enumerate(zip(topic_distributions1, topic_distributions2)):
    # Convert topic distributions to probability vectors
    topic_probs1 = [topic_prob[1] for topic_prob in doc1]
    topic_probs2 = [topic_prob[1] for topic_prob in doc2]

    # Calculate Hellinger distance
    hellinger_dist = hellinger(topic_probs1, topic_probs2)

    # Calculate Jensen-Shannon divergence
    js_divergence = jensenshannon(topic_probs1, topic_probs2)

    print(f"Document {i+1} Hellinger distance: {hellinger_dist:.4f}")
    print(f"Document {i+1} Jensen-Shannon divergence: {js_divergence:.4f}")

len(corpus_by_country)

from scipy.spatial.distance import jensenshannon
from scipy.special import kl_div
import numpy as np

# Initialize matrices to store pairwise divergences
jsd_matrix = np.zeros((17, 17))
kl_matrix = np.zeros((17, 17))

# Calculate divergences for each pair of subsets
for i, subset1 in enumerate(corpus_by_country):
    for j, subset2 in enumerate(corpus_by_country):
        # Get topic distributions for each subset
        topic_distributions1 = [lda_model.get_document_topics(doc, minimum_probability=0) for doc in corpus_by_country[subset1]]
        topic_distributions2 = [lda_model.get_document_topics(doc, minimum_probability=0) for doc in corpus_by_country[subset2]]

        # Convert topic distributions to probability vectors
        topic_probs1 = np.array([[topic_prob[1] for topic_prob in doc] for doc in topic_distributions1])
        topic_probs2 = np.array([[topic_prob[1] for topic_prob in doc] for doc in topic_distributions2])

        # Calculate average topic distributions for each subset
        avg_topic_probs1 = np.mean(topic_probs1, axis=0)
        avg_topic_probs2 = np.mean(topic_probs2, axis=0)

        # Calculate Jensen-Shannon divergence
        jsd_matrix[i, j] = np.mean([jensenshannon(p1, p2) for p1, p2 in zip(topic_probs1, topic_probs2)])

        # Calculate Kullback-Leibler divergence
        kl_matrix[i, j] = np.mean([np.sum(kl_div(p1, p2)) for p1, p2 in zip(topic_probs1, topic_probs2)])

# Print the matrices
print("Jensen-Shannon Divergence Matrix:")
print(len(jsd_matrix))
# print("\nKullback-Leibler Divergence Matrix:")
# print(kl_matrix)

import seaborn as sns
import matplotlib.pyplot as plt

# Transpose the matrices
jsd_matrix_transposed = jsd_matrix.T
#kl_matrix_transposed = kl_matrix.T

# Hierarchical clustering based on Jensen-Shannon Divergence
sns.clustermap(jsd_matrix_transposed, cmap="YlGnBu", figsize=(10, 10), method='average', metric='euclidean', row_cluster=True, col_cluster=True, dendrogram_ratio=(0.1, 0.2), xticklabels=countries, yticklabels=topics)
plt.title('Hierarchical Clustering Heatmap (Jensen-Shannon Divergence)')
plt.xlabel('Countries')
plt.ylabel('Topics')
plt.show()

# Hierarchical clustering based on Kullback-Leibler Divergence
# sns.clustermap(kl_matrix_transposed, cmap="YlGnBu", figsize=(10, 10), method='average', metric='euclidean', row_cluster=True, col_cluster=True, dendrogram_ratio=(0.1, 0.2), xticklabels=corpus_by_country.keys(), yticklabels=range(kl_matrix.shape[1]))
# plt.title('Hierarchical Clustering Heatmap (Kullback-Leibler Divergence)')
# plt.xlabel('Countries')
# plt.ylabel('Topics')
# plt.show()

range(jsd_matrix.shape[1])



import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

# Replace NaN values with zero and infinite values with a large finite value
jsd_matrix_fixed = np.nan_to_num(jsd_matrix, nan=0, posinf=1e9, neginf=-1e9)

# Calculate linkage matrix
Z_jsd = linkage(jsd_matrix_fixed, method='average')

# Plot the dendrogram
plt.figure(figsize=(10, 5))
plt.title('Hierarchical Clustering Dendrogram (Jensen-Shannon Divergence)')
plt.xlabel('Subsets')
plt.ylabel('Distance')
dendrogram(
    Z_jsd,
    labels=[f"Subset {i+1}" for i in range(17)],
    leaf_rotation=90.,
    leaf_font_size=12.
)
plt.show()

# import gensim

# # Dictionary to store topic distributions by country
# topic_distributions_by_country = {}

# # Train LDA models and calculate topic distributions for each country
# for country, country_corpus in corpus_by_country.items():
#     # Convert tuples back to strings
#     country_corpus = [[id2word[word_id] for word_id, freq in doc] for doc in country_corpus]

#     # Create the dictionary and corpus specific to this country
#     country_id2word = gensim.corpora.Dictionary(country_corpus)
#     country_corpus = [country_id2word.doc2bow(doc) for doc in country_corpus]

#     # Train the LDA model for this country
#     lda_model_country = gensim.models.ldamodel.LdaModel(corpus=country_corpus,
#                                                         id2word=country_id2word,
#                                                         num_topics=K_best,
#                                                         random_state=100,
#                                                         update_every=1,
#                                                         chunksize=50,
#                                                         passes=20,
#                                                         alpha='auto',
#                                                         per_word_topics=False)  # Change to False

#     # Get the topic distributions for this country
#     topic_distributions_by_country[country] = []

#     # Calculate topic distributions for each document in the country
#     for doc in country_corpus:
#         doc_topics = lda_model_country.get_document_topics(doc)
#         topic_distributions_by_country[country].append(doc_topics)

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

# Replace NaN values with zero and infinite values with a large finite value
jsd_matrix_fixed = np.nan_to_num(jsd_matrix, nan=0, posinf=1e9, neginf=-1e9)

# Calculate linkage matrix
Z_jsd = linkage(jsd_matrix_fixed, method='average')

# Plot the combined dendrogram and heatmap
fig, ax = plt.subplots(figsize=(10, 7))

# Plot dendrogram
dendrogram(
    Z_jsd,
    labels=[f"Subset {i+1}" for i in range(17)],
    leaf_rotation=90.,
    leaf_font_size=12.,
    ax=ax
)

# Plot heatmap of topic distributions
topics = [f"Topic {i+1}" for i in range(lda_model.num_topics)]
im = ax.imshow(jsd_matrix_fixed, cmap='viridis', aspect='auto')

# Add colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Jensen-Shannon Divergence')

# Set labels and ticks
ax.set_title('Hierarchical Clustering Dendrogram with Topic Heatmap')
ax.set_xlabel('Subsets')
ax.set_ylabel('Distance')
ax.set_xticks([])  # Remove x-axis ticks

plt.xticks(rotation=45)
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

# Replace NaN values with zero and infinite values with a large finite value
jsd_matrix_fixed = np.nan_to_num(jsd_matrix, nan=0, posinf=1e9, neginf=-1e9)

# Calculate linkage matrix
Z_jsd = linkage(jsd_matrix_fixed, method='average')

# Calculate the height of the dendrogram
n = 17
height = 0.2 * n

# Plot the combined dendrogram and heatmap
fig, ax = plt.subplots(figsize=(10, height))

# Plot dendrogram
dendrogram(
    Z_jsd,
    labels=[f"Subset {i+1}" for i in range(n)],
    leaf_rotation=90.,
    leaf_font_size=12.,
    ax=ax
)

# Plot heatmap of topic distributions with adjusted aspect ratio
topics = [f"Topic {i+1}" for i in range(lda_model.num_topics)]
im = ax.imshow(jsd_matrix_fixed, cmap='viridis', aspect=0.5)  # Adjust aspect ratio here

# Add colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Jensen-Shannon Divergence')

# Set labels and ticks
ax.set_title('Hierarchical Clustering Dendrogram with Topic Heatmap')
ax.set_xlabel('Subsets')
ax.set_ylabel('Distance')

# Add topic numbers
ax2 = ax.twinx()
ax2.set_yticks(np.linspace(0, len(jsd_matrix_fixed), lda_model.num_topics))
ax2.set_yticklabels(topics)

# Add number of topics
num_topics_text = f"Number of topics: {lda_model.num_topics}"
ax.text(1.02, 0.5, num_topics_text, transform=ax.transAxes, fontsize=12, ha='left')

plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to minimize whitespace
plt.show()

import matplotlib.pyplot as plt

def plot_topic_distribution(topic_distributions, country_name):
    num_docs = len(topic_distributions)
    topic_proportions = [0] * K_best

    for doc_topics in topic_distributions:
        for topic, proportion in doc_topics:
            topic_proportions[topic] += proportion / num_docs

    plt.bar(range(K_best), topic_proportions, tick_label=range(K_best))
    plt.title("Topic Distribution for {}".format(country_name))
    plt.xlabel("Topic")
    plt.ylabel("Proportion")
    plt.show()

# Plot topic distributions for each country
plot_topic_distribution(topic_distributions_by_country['Sweden'], 'Sweden')
plot_topic_distribution(topic_distributions_by_country['China'], 'China')

([[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['Sweden']])

# import numpy as np
# from scipy.cluster.hierarchy import dendrogram, linkage
# from scipy.spatial.distance import squareform
# from scipy.stats import entropy

# def jensen_shannon_divergence(p, q):
#     # Calculate Jensen-Shannon divergence
#     m = 0.5 * (p + q)
#     return 0.5 * (entropy(p, m) + entropy(q, m))

# # Convert topic distributions to numpy arrays
# data1 = [[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['Sweden']]
# data2 = [[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['China']]

# # Create a structured array with two fields: 'topic_id' and 'probability'
# dtype = [('topic_id', int), ('probability', float)]
# topic_distributions_country1 = np.array(data1, dtype=dtype)
# topic_distributions_country2 = np.array(data2, dtype=dtype)

# # print(np_array)
# # topic_distributions_country1 = np.array([[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['Sweden']])
# # topic_distributions_country2 = np.array([[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['China']])

# # Compute Jensen-Shannon divergence matrix
# def compute_jensen_shannon_matrix(topic_distributions1, topic_distributions2):
#     num_docs1 = len(topic_distributions1)
#     num_docs2 = len(topic_distributions2)

#     jensen_shannon_matrix = np.zeros((num_docs1, num_docs2))

#     for i, doc1 in enumerate(topic_distributions1):
#         for j, doc2 in enumerate(topic_distributions2):
#             p = np.array([proportion for _, proportion in doc1])
#             q = np.array([proportion for _, proportion in doc2])
#             jensen_shannon_matrix[i, j] = jensen_shannon_divergence(p, q)

#     return jensen_shannon_matrix

# jensen_shannon_matrix = compute_jensen_shannon_matrix(topic_distributions_country1, topic_distributions_country2)

# # Perform hierarchical clustering
# Z = linkage(squareform(jensen_shannon_matrix), method='average')

# # Plot dendrogram
# plt.figure(figsize=(10, 6))
# plt.title('Hierarchical Clustering Dendrogram')
# plt.xlabel('Country')
# plt.ylabel('Distance')
# dendrogram(Z, labels=['Sw']*len(topic_distributions_country1) + ['Ch']*len(topic_distributions_country2))
# plt.show()

[[(topic, proportion) for topic, proportion in doc_topics] for doc_topics in topic_distributions_by_country['China']]

import numpy as np

data = [[(9, 0.99987715)], [(3, 0.99980885)]]

# Create a structured array with two fields: 'topic_id' and 'probability'
dtype = [('topic_id', int), ('probability', float)]
np_array = np.array(data, dtype=dtype)

print(np_array)

a = 0
for country1, dist1 in topic_distributions_by_country.items():
    print(country1, 'and',dist1)
    row = []
    for country2, dist2 in topic_distributions_by_country.items():
        # Extract topic probabilities from distributions
        probs1 = [topic_prob for topic_prob in dist1]
        probs2 = [topic_prob for topic_prob in dist2]
        # print(probs1)
        # print(probs2)
        a+=1

corpus_by_country

def plot_difference_plotly(mdiff, title="", annotation=None):
    """Plot the difference between models.

    Uses plotly as the backend."""
    import plotly.graph_objs as go
    import plotly.offline as py

    annotation_html = None
    if annotation is not None:
        annotation_html = [
            [
                "+++ {}<br>--- {}".format(", ".join(int_tokens), ", ".join(diff_tokens))
                for (int_tokens, diff_tokens) in row
            ]
            for row in annotation
        ]

    data = go.Heatmap(z=mdiff, colorscale='RdBu', text=annotation_html)
    layout = go.Layout(width=950, height=950, title=title, xaxis=dict(title="topic"), yaxis=dict(title="topic"))
    py.iplot(dict(data=[data], layout=layout))


def plot_difference_matplotlib(mdiff, title="", annotation=None):
    """Helper function to plot difference between models.

    Uses matplotlib as the backend."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(18, 14))
    data = ax.imshow(mdiff, cmap='RdBu_r', origin='lower')
    plt.title(title)
    plt.colorbar(data)


try:
    get_ipython()
    import plotly.offline as py
except Exception:
    #
    # Fall back to matplotlib if we're not in a notebook, or if plotly is
    # unavailable for whatever reason.
    #
    plot_difference = plot_difference_matplotlib
else:
    py.init_notebook_mode()
    plot_difference = plot_difference_plotly

mdiff, annotation = lda_fst.diff(lda_snd, distance='jaccard', num_words=50)
plot_difference(mdiff, title="Topic difference (two models)[jaccard distance]", annotation=annotation)

import gensim

# Dictionary to store differences in topic distributions by country
country_differences = {}

# Iterate over pairs of countries
for country1, dist1 in topic_distributions_by_country.items():
    for country2, dist2 in topic_distributions_by_country.items():
        # Skip if the same country or if already processed
        if country1 == country2 or (country2, country1) in country_differences:
            continue

        # Compute difference between topic distributions of country1 and country2
        mdiff, annotation = dist1.diff(dist2, distance='jaccard', num_words=50)

        # Store difference in country_differences dictionary
        country_differences[(country1, country2)] = {'mdiff': mdiff, 'annotation': annotation}

# Now country_differences contains the differences in topic distributions between each pair of countries

# from scipy.stats import entropy

# # Compute pairwise KL divergence between countries
# kl_divergence_list = []

# for i in range(len(countries)):
#     for j in range(i + 1, len(countries)):
#         country1 = countries[i]
#         country2 = countries[j]

#         # Check if the number of topics for both countries is the same
#         if topic_distributions_by_country[country1].shape[1] != topic_distributions_by_country[country2].shape[1]:
#             print(f"Number of topics for {country1} and {country2} do not match. Skipping...")
#             continue

#         # Calculate KL divergence only if the countries are different
#         kl_div = entropy(topic_distributions_by_country[country1].mean(axis=0),
#                          qk=topic_distributions_by_country[country2].mean(axis=0))
#         kl_divergence_list.append(kl_div)

# # Convert list to numpy array
# kl_divergence_matrix = np.array(kl_divergence_list).reshape(len(countries), len(countries))

# # Step 4: Hierarchical clustering
# linkage_matrix = hierarchy.linkage(kl_divergence_matrix, method='average')

# # Step 5: Visualize dendrogram
# plt.figure(figsize=(10, 6))
# dendrogram = hierarchy.dendrogram(linkage_matrix, labels=countries, orientation='left', leaf_font_size=10)
# plt.xlabel('Distance')
# plt.ylabel('Country')
# plt.title('Hierarchical Clustering of Countries based on Topic KL Divergence')
# plt.grid(True)
# plt.show()

import pandas as pd
import plotly.graph_objects as go

# Example data (replace with your data)
data = {
    'Topic1': [0.2, 0.3, 0.1, 0.5],
    'Topic2': [0.1, 0.4, 0.2, 0.3],
    'Topic3': [0.3, 0.2, 0.4, 0.1],
}

df = pd.DataFrame(data, index=['RegionA', 'RegionB', 'RegionC', 'RegionD'])

# Create the heatmap
fig = go.Figure(data=go.Heatmap(
                   z=df.values,
                   x=list(df.columns),
                   y=list(df.index),
                   colorscale='Viridis'))

# Update layout
fig.update_layout(
    title='Clustergram for Topics and Regions',
    xaxis=dict(title='Topics'),
    yaxis=dict(title='Regions'),
    width=700,
    height=500,
    plot_bgcolor='#FFFFFF'  # Change plot background color
)

# Show the plot
fig.show()

# Initialize an empty list to store document-topic distributions
document_topic_distributions = []

# Loop through all documents in the corpus
for doc_id in range(len(corpus)):
    doc_topics = lda_model.get_document_topics(corpus[doc_id], minimum_probability=0.0)
    document_topic_distributions.append(doc_topics)



