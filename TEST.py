import telebot
import requests, json 
import gspread
import datetime
import random
import os
from flask import Flask,request
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('', scope)#import your json credential files
client = gspread.authorize(creds)

sheet = client.open("DATA").sheet1
user = {}
TOKEN = ""#import your telegram token
bot = telebot.TeleBot(TOKEN)
pixsbay = ""#import your picsbay token
server=Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	global user
	user[str(message.from_user.id)]={"search" : False}
	#print(message.text)
	bot.reply_to(message, "Howdy, how are you doing?\n Type /search to begin")

@bot.message_handler(commands=['search'])
def send_info(message):
   global user
   text = (
   message.chat.first_name+" You have logged in\nStart searching"
   )
   user[str(message.from_user.id)]={"search" : True}
   print("status:::",user[str(message.from_user.id)])
   print("\n\n\n", message.chat.first_name)
   #bot.send_message(message.chat.id, text, parse_mode='HTML')
   bot.reply_to(message,text)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	print(message)
	global user
	if(user[str(message.from_user.id)]["search"]):
		api_key = ""#import your open weather api
  
		base_url = "http://api.openweathermap.org/data/2.5/weather?"

		city_name = message.text

		complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
   

		response = requests.get(complete_url) 
	#print(response.json)
	
		x = response.json() 
	#print(x)
		if(x['cod']==200):
			size = x['weather'][0]['description'].split(' ')
			print(size)
		#print("size:::",len(size))
			if(len(size)<=2):
				if(x['weather'][0]['description'] not in "moderate rain"):
					pixs = requests.get("https://pixabay.com/api/?key={}&q={}&image_type=photo".format(pixsbay,x['weather'][0]['description']))
				else:
					pixs = requests.get("https://pixabay.com/api/?key={}&q={}&image_type=photo".format(pixsbay,"raining"))

			else:

				sliced = x['weather'][0]['description'].split(' ')
			#print("sliced",sliced[-2:])
				descrip = sliced[-2]+" "+sliced[-1]
			#print("descr",descrip)
				pixs = requests.get("https://pixabay.com/api/?key={}&q={}&image_type=photo".format(pixsbay,descrip))
				print("https://pixabay.com/api/?key={}&q={}&image_type=photo".format(pixsbay,descrip))
			pictures = pixs.json()
			limit = 0
		#print("Respinse::::",pictures)
			temp = round(x['main']['temp']-273.15,2)
			print("total hits::",len(pictures['hits']))
			if(len(pictures['hits'])<=1):
				limit = 0
			else:
				total_results = len(pictures['hits'])
				n = random.randint(0,int(total_results))
				limit = int(n)
				if(limit == total_results):
					limit=limit-1
				print("limit",n)
				print(pictures['hits'][limit]['largeImageURL'])
			
			print("random:::",limit)
			info = "The weather in {} is {} \nTEMPERATURE : {}'C".format(message.text,x['weather'][0]['description'],temp)
	#print(message.chat.id)
			y = pixs.json()
	#print(y)
			d = datetime.datetime.now()
			sheet.append_row([str(d),message.chat.id,message.chat.first_name,message.text,x['weather'][0]['description'],y['hits'][int(limit)]['largeImageURL']])
		#print(message)
			user[str(message.from_user.id)]={"search" : False}
			bot.send_photo(message.chat.id,y['hits'][int(limit)]['largeImageURL'])
			bot.send_message(message.chat.id,info)
			
		
		else:
			bot.reply_to(message,"Improper input")
	else:
		bot.reply_to(message,"Login to begin searching\nType /search to login")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
   bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
   return "!", 200
@server.route("/")
def webhook():
   bot.remove_webhook()
   bot.set_webhook(url="" + TOKEN) #ADD YOUR WEBHOOK URL
   return "!", 200
if __name__ == "__main__":
   server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))