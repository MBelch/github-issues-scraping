from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

# defining functions which we'll use in the main program
def get_url_pages(main_url, n):
	pages_urls = []
	for i in range(1,n):
		pages_urls.append(main_url+'?page='+str(i)+'&q=is%3Aissue+is%3Aclosed')
	return(pages_urls)

def get_pages_response(list_urls):
	responses = []
	for e in list_urls:
		r = requests.get(e)
		if(r.status_code == 200):
			responses.append(r)
	return(responses)    

def get_tags(pages_responses, tag, tag_class):
	tags = []
	for response in pages_responses:
		doc = BeautifulSoup(response.text, 'html.parser')
		tags += doc.find_all(tag, {'class': tag_class})
	return tags


#Main program:
if __name__ == "__main__":
	
	#declaring empty lists as variables
	authors = []
	labels = []
	time = []

	#Using functions defined above
	pages_response = get_pages_response(get_url_pages('https://github.com/rails/rails/issues',26))
	gt = get_tags(pages_response,"div","flex-auto min-width-0 p-2 pr-3 pr-md-2")

	#Loading the list "authors" with the issues authors
	for e in gt:
		authors.append((e.find("a","Link--muted")).text)

    #Loading the list "labels" with the issues labels
	for l in gt:
		try:
			elt = str((l.find("a","IssueLabel hx_IssueLabel")).text)
			elt = re.sub('\n',"",elt)
			elt = elt.strip()
			labels.append(elt)
        
		except AttributeError:
			labels.append(None)

    #Loading the list "time" with the datetime of each issue
	for t in gt:
		time.append((t.find("relative-time", "no-wrap")).get('datetime'))

    #Generating a dataframe
	dic = {"authors" : authors}
	df = pd.DataFrame(data = dic)
	df['labels'] = labels
	df['datetime'] = time
	df['datetime'] = df['datetime'].astype('datetime64[ns]')

	#Spliting the datetime to a date part and time part
	df['date'] = pd.to_datetime(df['datetime']).dt.date
	df['time'] = pd.to_datetime(df['datetime']).dt.time

	#Ploting the data vizs
	sns.set()
	print("\n\n================================> Chart plotting <===============================")
	print("\n\nFor a line chart of number of issues by date, press 1")
	print("For a bar chart of top 5 authors, press 2")
	print("For a bar chart of top 5 labels, press 3")
	print("Press any to exit")
	print("\n\n=================================================================================\n")
	
	i = 1
	try:
		while(i in (1,2,3)):
		
			i = int(input("================> Type here and insert: "))
			if(i == 1):
				df_groupby_date = df.groupby(by = 'date').count()
				x = df['date'].drop_duplicates()
				y_mean = [np.mean(df_groupby_date["authors"])]*len(x)
				y = df_groupby_date["authors"]
				print("Statistics about the number of authors")
				print(y.describe())
				print("\n\n")
				fig,ax = plt.subplots()
				ax.plot(y, label='Number of issues', marker='o')
				ax.plot(x,y_mean, label='Mean', linestyle='--')
				ax.legend(loc='upper right')
				plt.show()

			elif(i == 2): 
				df_group_by_authors = df.groupby(by = 'authors').count()
				df2 = df_group_by_authors.sort_values('datetime',ascending = False).head(5)
				df2["datetime"].plot(kind = 'bar', color = 'r')
				plt.title("Top 5 issues reporters")
				plt.ylabel('Number of issues')
				plt.xlabel('Authors')
				plt.show()

			elif(i == 3):
				df_group_by_labels = df.groupby(by = 'labels').count()
				df2 = df_group_by_labels.sort_values('datetime',ascending = False).head(5)
				df2["datetime"].plot(kind = 'bar', color = 'g')
				plt.show()

			else:
				print("\n\nexiting!!")

	except ValueError:
		print("\n\nexiting!!")
		