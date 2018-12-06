# Streaming Tweets with ElasticSearch and Kibana

 This solution helps you to listen to keywords (similar to twitter search for keywords) and stream related tweets in near real time, onto a Kibana Dashboard. 

Requirements:
- ElasticSearch, Kibana
- Python 3.6 installed with ElasticSearch and Tweepy Python APIs


To deploy this solution follow the below steps,
1. Setup ElasticSearch and Kibana in the host machine.
		Follow official doc, based on the OS of your machine,
			[ElasticSearch Installation Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html)
			[Kibana Installation Reference](https://www.elastic.co/guide/en/kibana/6.5/setup.html)
2. Configure and run [stream_tweets.py](https://gitlab.com/dineshbabur92/kibana_stream_tweets/stream_tweets.py)
		Install	required packages and change configurations as per instructions given in the code on top.
		Run 'python stream_tweets.py', preferably in the background, as this program runs in an infinite loop to fetch tweets continously.
3. Open Kibana in the web browser (http://<ip_of_host_machine>:5601) and start creating dashboards.
		[Kibana Dashboarding Reference](https://www.elastic.co/guide/en/kibana/current/tutorial-build-dashboard.html)
	
[This document]() has snapshots of a sample dashboard with near-real-time tweets and hightlighting features in the dashboard.
