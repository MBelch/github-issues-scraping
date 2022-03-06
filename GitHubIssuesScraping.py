from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

# defining functions which we'll use in the main program
def get_url_pages(main_url, n, status):
	pages_urls = []
	if(status.lower() == "closed"):
		for i in range(1,n):	
			pages_urls.append(main_url+'?page='+str(i)+'&q=is%3Aissue+is%3Aclosed')

	elif(status.lower() == "opened"):
		for i in range(1,n):
			pages_urls.append(main_url+'?page='+str(i)+'&q=is%3Aissue+is%3Aopen')

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

def get_authors_issues(tags_list):
	authors = []
	for e in tags_list:
		authors.append((e.find("a","Link--muted")).text)
	return authors

def get_labels_issues(tags_list):
	labels = []
	for l in tags_list:
		try:
			elt = str((l.find("a","IssueLabel hx_IssueLabel")).text)
			elt = re.sub('\n',"",elt)
			elt = elt.strip()
			labels.append(elt)
        
		except AttributeError:
			labels.append(None)
	return labels

def get_time_issues(tags_list):
	time = []
	for t in tags_list:
		time.append((t.find("relative-time", "no-wrap")).get('datetime'))
	return time


#Main program:
if __name__ == "__main__":
	
	#declaring empty lists as variables
	authors = []
	labels = []
	time = []
	authors_opened = []
	labels_opened = []
	time_opened= []

	#Using functions defined above
	#Getting the first 26 pages of closed issues and for all the opened issues
	pages_response = get_pages_response(get_url_pages('https://github.com/rails/rails/issues',25,"closed"))
	gt = get_tags(pages_response,"div","flex-auto min-width-0 p-2 pr-3 pr-md-2")
	pages_response_opened = get_pages_response(get_url_pages('https://github.com/rails/rails/issues',25,"opened"))
	gt_opened = get_tags(pages_response_opened,"div","flex-auto min-width-0 p-2 pr-3 pr-md-2")

	#Loading the list "authors" with the issues authors
	authors = get_authors_issues(gt)
	authors_opened = get_authors_issues(gt_opened)

	#Loading the list "labels" with the issues labels
	labels = get_labels_issues(gt)
	labels_opened = get_labels_issues(gt_opened)

	#Loading the list "time" with the datetime of each issue
	time = get_time_issues(gt)
	time_opened = get_time_issues(gt_opened)

	#Generating a dataframe for the closed issues
	dic = {"authors" : authors}
	df = pd.DataFrame(data = dic)
	df['labels'] = labels
	df['datetime'] = time
	df['datetime'] = df['datetime'].astype('datetime64[ns]')

	#Generating a dataframe for the opened issues
	dic_opened = {"authors" : authors_opened}
	df_opened = pd.DataFrame(data = dic_opened)
	df_opened['labels'] = labels_opened
	df_opened['datetime'] = time_opened
	df_opened['datetime'] = df_opened['datetime'].astype('datetime64[ns]')	

	#Spliting the datetime to a date part and time part for the closed issues
	df['date'] = pd.to_datetime(df['datetime']).dt.date
	df['time'] = pd.to_datetime(df['datetime']).dt.time
	df['month'] = pd.to_datetime(df['datetime']).dt.month

	#Spliting the datetime to a date part and time part for the opened issues
	df_opened['date'] = pd.to_datetime(df_opened['datetime']).dt.date
	df_opened['time'] = pd.to_datetime(df_opened['datetime']).dt.time
	df_opened['year'] = pd.to_datetime(df_opened['datetime']).dt.year

	#Number of issues scrapped
	print("\n\nNumber of closed issues scrapped : ", len(df))
	print("Number of opened issues scrapped : ", len(df_opened))

	#Ploting the data vizs
	sns.set()
	print("\n\n================================> Chart plotting <===============================")
	print("\n\nFor a line chart of number of the closed issues by date, press 1")
	print("For a bar chart of top 5 authors of the closed issues, press 2")
	print("For a bar chart of top 5 labels of the closed issues, press 3")
	print("For a bar chart representing number of closed issues by months, press 4")
	print("For a bar chart representing number of opened issues by years, press 5")
	print("Press any to exit")
	print("\n\n=================================================================================\n")
	
	i = 1
	try:
		while(i in (1,2,3,4,5)):
		
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
				df2["datetime"].plot(kind = 'barh', color = 'r')
				plt.title("Top 5 issues reporters")
				plt.xlabel('Number of issues')
				plt.ylabel('Authors')
				plt.show()

			elif(i == 3):
				df_group_by_labels = df.groupby(by = 'labels').count()
				df2 = df_group_by_labels.sort_values('datetime',ascending = False).head(5)
				df2["datetime"].plot(kind = 'barh', color = 'g')
				plt.xlabel('Number of issues')
				plt.show()

			elif(i == 4):
				df_group_by_months = df.groupby(by = 'month').count()
				df_group_by_months["datetime"].plot(kind = 'bar', color = 'y')
				plt.ylabel('Number of issues')
				plt.show()

			elif(i == 5):
				df_group_by_year = df_opened.groupby(by = 'year').count()
				df_group_by_year["datetime"].plot(kind = 'bar', color = 'm')
				plt.ylabel('Number of opened issues')
				plt.show()				

			else:
				print("\n\nexiting!!")

	except ValueError:
		print("\n\nexiting!!")