import pandas as pd
import numpy as np
import re, nltk
import texts

import coach_matic_base

my_stopwords = {"PT": ["ser", "usuário", "requisito", "requisitos", "nessa", "pode", 
                "protótipo", "caso", "deveria", "poderia", "como", "quero",
                "então", "dado", "quando", "podem", "favor", "png", "gif", 
                "poderiam", "gentileza", "segue", "anexo", "usando", "existente"],
                "EN": ["user", "requirement", "this", "can", "may", "prototype",
                       "case", "should", "as", "how", "want", "given", "please",
                       "png", "gif", "attached", "attach", "using", "existing",
                       "else"]}

def get_client_stopwords(config):
    client_stopwords = my_stopwords[config.language].copy()
    for new_word in config.bag_of_words_exclude.split(","):
        client_stopwords.append(new_word.lower().strip())
    return client_stopwords
        
# TODO: remove in EN also...
def remove_plural(df_words):
    df_words = df_words.sort_values(by="Word")
    for idx in range(0, len(df_words) - 1):
        cur_word = df_words.iloc[idx]["Word"]
        next_word = df_words.iloc[idx + 1]["Word"]
        is_plural = (cur_word + "s" == next_word) or \
                    (cur_word[-2:] == "ão" and next_word[-3:] == "ões") or \
                    (cur_word[-2:] == "il" and next_word[-3:] == "eis")

        if is_plural:
            df_words.iloc[idx + 1]["Word"] = cur_word
            
    return df_words

def break_words(text):
    if text == None:
        return []
    
    original = text
    
    # text = "* Integrar o Swagger e config pagamento_cancelamento"
    # text = "Tests: 285,    Assertions: 1211{noformat}"
    # text = "abc contestação def"
    # text = "HomologaÃ§Ã£o do Sistema - MigraÃ§Ã£o Sul RegressÃ£o: https://docs.google.com/spreadsheets/d/11ykVgCp1QVrPJf5wdYdywQsRrIcsscaA/edit#gid=1472526132 https://docs.google.com/spreadsheets/d/11ykVgCp1QVrPJf5wdYdywQsRrIcsscaA/edit#gid=1472526132RegressÃ£o: https://docs.google.com/spreadsheets/d/11ykVgCp1QVrPJf5wdYdywQsRrIcsscaA/edit#gid=1472526132"
    text = text.lower()
    text = re.sub(r'http[^ ]*', '', text) # url
    text = re.sub(r'\{[^\}]*\}', '', text) # remove {...}
    text = re.sub(r'\[[^\]]*\]', '', text) # remove [...]
    # text = re.sub(r'[\:\,\.\!\?\d]', '', text) # remove :,.!? and numbers
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text) # remove everything is not letters
    text = re.sub(r'[\d_]', ' ', text) # remove digits
    text = re.sub(r'\s+', ' ', text) # remove double space
    
    all_words = text.strip().split(" ")

    for word in all_words:
        if word == "wdydywqsrricsscaa" or word == "qvrpjf":
            coach_matic_base.print_and_log("WORD_OF_BAGS: {} - original: {}".format(text, original))
        
    return all_words

def all_texts_from_history(issue):
    all_texts = ""
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == "description":
                all_texts += item.toString

    return all_texts
    
###########################################################################
# tasks analysis
def count_words(config, df, all_issues, all_subtasks):
    client_stopwords = get_client_stopwords(config)
    
    nltk.download('stopwords')
    if config.language == "EN":
        stopwords = nltk.corpus.stopwords.words('english')
    else:
        stopwords = nltk.corpus.stopwords.words('portuguese')

    df_cycletime = (df[["Key", "BagWordsAxis"]].copy()).dropna()
    df_words = pd.DataFrame(columns=["Key", "BagWordsAxis", "Word", "Count"])
    
    for issue in all_issues + all_subtasks:
        if issue in all_subtasks:
            key = issue.fields.parent
        else:
            key = issue.key
        
        try:
            df_info = df_cycletime[df_cycletime["Key"] == key]["BagWordsAxis"]
            
            if len(df_info) > 0 and df_info.iloc[0] != None:
                cycletime = df_info.iloc[0]
                all_words = break_words(issue.fields.summary + " " + 
                                        issue.fields.description + " " + 
                                        all_texts_from_history(issue))
                
                all_words_set = set(all_words)
                
                for word in all_words_set:
                    if word not in stopwords and \
                            word not in client_stopwords and \
                            len(word) > 2:
                        d = {"Key": key,
                              "BagWordsAxis": cycletime,
                              "Word": word, 
                              "Count": 1}
                        df_words = coach_matic_base.concat(df_words, d)
        except Exception as e:
            print(e)
            print("faio count_words para key: {}".format(key))
    
    return remove_plural(df_words)
    # return df_words

# investigate which words have more appearance among items with more cycle time
# it becomes a candidate if it has more presente on higher percentiles and less presence
# on lower percentiles
# (this is to avoid too common words, apearing in all items)
def bag_words_analysis(final_result, config, df, all_issues, all_subtasks):
    df_words = count_words(config, df, all_issues, all_subtasks)
    df_cycletimes = (df["BagWordsAxis"].copy()).dropna()
    
    word_per_percentil = {}
    cycletime_percentil = []
    
    all_percentiles = [90, 85, 75, 50, 0]
    
    # look for words with most appearance in first percentiles
    for percentile in all_percentiles[:3]:
        if len(df_cycletimes) == 0:
            continue
        
        cycletime_pct = np.percentile(df_cycletimes, percentile, interpolation="higher")
        
        cycletime_percentil.append(cycletime_pct)

        df_pct = df_words[df_words["BagWordsAxis"] >= cycletime_pct][["Word", "Count"]]
        df_most_words = df_pct.groupby(by="Word").sum()
        df_most_words = df_most_words.sort_values(by="Count", ascending=False)
        
        num_issues_pct = len(df_words[df_words["BagWordsAxis"] >= cycletime_pct]["Key"].unique())
        
        indexes = list(df_most_words.index)
        i = 0
        pct_issues = 100
        while i < len(indexes) and pct_issues >= 50:
            word = indexes[i]
            num_issues_word = len(df_words[(df_words["BagWordsAxis"] >= cycletime_pct) &
                                           (df_words["Word"] == word)]["Key"].unique())
            pct_issues = (num_issues_word / num_issues_pct) * 100
            
            if word not in word_per_percentil:
                word_per_percentil[word] = {}
            word_per_percentil[word][percentile] = pct_issues
            
            i += 1
            
    # get occurrence for words found loop before
    for percentile in all_percentiles[3:]:
        cycletime_pct = np.percentile(df_cycletimes, percentile, interpolation="lower")
        
        cycletime_percentil.append(cycletime_pct)
        
        num_issues_pct = len(df_words[df_words["BagWordsAxis"] >= cycletime_pct]["Key"].unique())
        
        for word in word_per_percentil.keys():
            num_issues_word = len(df_words[(df_words["BagWordsAxis"] >= cycletime_pct) & 
                                          (df_words["Word"] == word)]["Key"].unique())
            pct_issues = (num_issues_word / num_issues_pct) * 100

            word_per_percentil[word][percentile] = pct_issues


    # set final availation
    if config.bag_of_words_axis == "CycleTime":
        result = texts.bagwords_title_cycletime
    elif config.bag_of_words_axis == "timespent":
        result = texts.bagwords_title_timespent
    elif config.bag_of_words_axis == "aggregatetimespent":
        result = texts.bagwords_title_aggregatedtimespent
    
    text_count_words = ""
    for i in range(len(all_percentiles)):
        percentile = all_percentiles[i]
        cycletime_pct = cycletime_percentil[i]
        
        num_issues_pct = len(df_words[df_words["BagWordsAxis"] >= cycletime_pct]["Key"].unique())
        
        for word in word_per_percentil.keys():
            if percentile in word_per_percentil[word]:
                word_pct = word_per_percentil[word][percentile]
            else:
                # recount if not found %
                num_issues_word = len(df_words[(df_words["BagWordsAxis"] >= cycletime_pct) & 
                                              (df_words["Word"] == word)]["Key"].unique())
                word_pct = (num_issues_word / num_issues_pct) * 100
                word_per_percentil[word][percentile] = word_pct
                
            text_count_words += texts.bagwords_count.format(word)
        
        text_count_words += "<br/>"
    
    words_to_investigate = ""
    max_pct_considered = 70
    
    # keeps iterating until find interesting words
    while max_pct_considered > 30 and words_to_investigate == "":
        for word in list(word_per_percentil.keys()):
            max_pct = max(word_per_percentil[word][all_percentiles[0]],
                          word_per_percentil[word][all_percentiles[1]])
            min_pct = min(word_per_percentil[word][all_percentiles[2]],
                          word_per_percentil[word][all_percentiles[3]])
            if max_pct / 3 > min_pct and max_pct > max_pct_considered:
                words_to_investigate += texts.bagwords_words.format(word)
            else:
                del word_per_percentil[word]
                
        max_pct_considered -= 10
            
    if words_to_investigate != "":
        result += texts.bagwords_investigate.format(words_to_investigate)
    else:
        result += texts.bagwords_not_found
        
    result += texts.bagwords_foot
    
    final_result.text_result["bag_of_words"] = result
    
    return df_words

#######################################################################
# sum cycletime per words      
def words_analysis_sum(final_result, config, df_words):
    result = ""
    percentile = 85
    
    df_words_aging = df_words.groupby(by="Word")["BagWordsAxis"].sum()
    df_words_aging = df_words_aging.to_frame()
    df_words_aging["Word"] = df_words_aging.index
    df_words_aging["BagWordsAxis"] = df_words_aging["BagWordsAxis"].astype("float")
    
    aging_pct = np.percentile(df_words_aging["BagWordsAxis"], percentile, interpolation="higher")

    if config.bag_of_words_axis == "CycleTime":
        day_or_hour = texts.total_aging_day
    else:
        day_or_hour = texts.bagwords_hour
        
    most_words = df_words_aging[df_words_aging["BagWordsAxis"] > aging_pct][["BagWordsAxis", "Word"]]
    most_words = most_words.sort_values(by="BagWordsAxis", ascending=False)
    list_of_words = []
    for idx in range(min(len(most_words), 15)):
        list_of_words.append("{}<font color=\"gray\">: {:.0f} {}</font>".format(
            most_words["Word"].iloc[idx], most_words["BagWordsAxis"].iloc[idx],
            day_or_hour))
        
    if config.bag_of_words_axis == "CycleTime":
        result = texts.bagwords_title_sum_cycletime
    elif config.bag_of_words_axis == "timespent":
        result = texts.bagwords_title_sum_timespent
    elif config.bag_of_words_axis == "aggregatetimespent":
        result = texts.bagwords_title_sum_aggregatedtimespent
        
    result += ", ".join(list_of_words) + "<br/>"
    final_result.text_result["sum_words_per_cycletime"] = result
    
def bag_words(final_result, config, df, all_issues, all_subtasks):
    if config.bag_of_words_axis == "CycleTime":
        df["BagWordsAxis"] = df["CycleTime"]
    else:
        df["BagWordsAxis"] = df[config.bag_of_words_axis_friendly] / (1*1)
        
    df_words = bag_words_analysis(final_result, config, df, all_issues, all_subtasks)
    words_analysis_sum(final_result, config, df_words)

    if config.bag_of_words_axis != "CycleTime":
        final_result.text_result["total_spenttime"] = texts.bagwords_total_spenttime.format(config.bag_of_words_axis_friendly,
                                                                                            int(df["BagWordsAxis"].sum()))