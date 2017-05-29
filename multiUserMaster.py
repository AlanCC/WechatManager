#coding=utf8
import itchat
from itchat.content import *
import re
import sys
from secretary import analyze,ifPersonalInfo,analyzeJunk
from check_pic import init, check_image

itchat.auto_login(hotReload=False)

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
	sendBackUser = itchat.search_friends(name=sys.argv[1])#.decode("utf8"))
	UserID = sendBackUser[0]['UserName']
	if(msg['FromUserName'] == UserID):
		print('Master received a message from slave')
		return					# if the message is from the slave, we believe it is safe
	if msg['MsgType'] == 1:
		print('Master Recieved a text message!')
		textContent = msg['Text']
		if (msg['FromUserName'] != itchat.originInstance.storageClass.userName) and (analyze(textContent, 0)):
			itchat.send(u'您可能在和“%s”的聊天中被询问私人信息，请注意防范 聊天内容为：\n\n%s' % (msg['User']['NickName'], msg['Text']), UserID)
		elif (msg['FromUserName'] == itchat.originInstance.storageClass.userName) and (ifPersonalInfo(textContent)):
			itchat.send(u'您可能在和“%s”的聊天中泄露了私人信息，请注意防范 聊天内容为：\n\n%s\n\n请及时撤回' % (msg['User']['NickName'], msg['Text']), UserID)
	if msg['MsgType'] == 49:
		print('Master recieved a notification!')
		titleContent = msg['FileName']
		snippetContent = msg['Content']
		if analyzeJunk(titleContent) or re.findall(snippetContent):
			print('Master received an annoying notification!')
			itchat.send(u'您在和“%s”的聊天中收到一条垃圾推送，其标题为：\n\n%s\n\n请 \
			注意钱包安全\ue409' % (msg['User']['NickName'], titleContent), UserID)

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
	#print(msg)
	sendBackUser = itchat.search_friends(name=sys.argv[1])#.decode("utf8"))
	UserID = sendBackUser[0]['UserName']
	msg.fileName = msg.fileName[:-3] + 'jpeg'
	input_file = './' + msg.fileName
	msg.download(msg.fileName)
	num = check_image(input_file, caffe_transformer,nsfw_net)
	print(num)
	if num >= 0.5:
		itchat.send(u'您在和“%s”的聊天中收到一条敏感图片，请谨言慎行\ue409' % (msg['User']['NickName']), UserID)
	else:
		print('not')


@itchat.msg_register([TEXT, SHARING], isGroupChat=True)
def groupchat_reply(msg):
	sendBackUser = itchat.search_friends(name=sys.argv[1])
	UserID = sendBackUser[0]['UserName']
	if msg['MsgType'] == 1:
		print('Recieve a text message!')
		textContent = msg['Text']
		if (msg['FromUserName'] != itchat.originInstance.storageClass.userName) and (analyze(textContent, 0)):
			itchat.send(u'您在群聊“%s”中被“%s”被询问私人信息，请注意防范。聊天内容为：\n\n%s\n\n请及时撤回' % (msg['User']['NickName'], msg['ActualNickName'], msg['Content']), UserID)
		elif (msg['FromUserName'] == itchat.originInstance.storageClass.userName) and ifPersonalInfo(textContent):
			itchat.send(u'您在群聊“%s”中向“%s”泄露了私人信息，请注意防范。聊天内容为：\
				\n\n%s\n\n请及时撤回' % (msg['User']['NickName'], msg['ActualNickName'], msg['Content']), UserID)

	if msg['MsgType'] == 49:
		print('Recieve a notification!')
		titleContent = msg['FileName']
		snippetContent = msg['Content']
		if analyzeJunk(titleContent) or re.findall(snippetContent):
			print('annoying notification detected!')
			itchat.send(u'您在群聊“%s”中收到“%s”的一条垃圾推送，其标题为：\n\n%s\n\n请 \
			注意钱包安全\ue409' % (msg['User']['NickName'], msg['ActualNickName'], titleContent), UserID)

[caffe_transformer,nsfw_net] = init()
itchat.run()
