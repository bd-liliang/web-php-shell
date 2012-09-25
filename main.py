# -*- coding:utf-8 -*
import tornado.ioloop
import tornado.httpserver
import tornado.web

import uuid
import json

from phpshell import PHPShell,PHP_VERSION_INFO

PHPSHELLS = {}

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		uid = str(uuid.uuid1())
		PHPSHELLS[uid] = PHPShell()

		templates = """
		<html>
			<head><title>web php shell! -- Powered By Lee</title></head>
			<script type="text/javascript"src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.0/jquery.min.js"></script>
			<style>
			*{
				font-family:Verdana;
			}
			textarea{
				color:white;
				background-color:black;
				font-size:12px;
			}
			.prompt, #output {
  				width: 45em;
				border: 1px solid silver;
  				margin: 0.5em;
  				padding: 0.5em;
  				padding-right: 0em;
				float:left;
				overflow-y:hidden;overflow:hidden;
			}
			#input{
				clear:both;
				margin-left:6px;
			}
			#input textarea{
				margin:0;
				height:70px;
				line-height:20px;
			}
			#output{
				color:white;
				background-color:black;
				font-size:12px;
				height:300px;
			}
			#output p{
				height:15px;
				line-height:15px;
				margin:0;
			}
			#output pre{
				margin:0;
			}
			</style>
			<script>
			var uid = '%s';
			$(document).ready(function(){
				$("#ip").keydown(function(e){ 
					var curKey = e.which; 
					if(curKey == 13){
						command = $("#ip").val();
						$("#ip").val('');
						//$("#output").append("php>>" + command + "\\n");
						$.get('/statement',{u:uid,c:command},function(data){
							eval('var resp = ' + data + ';');
							$("#output").append('<p>php&gt;&gt;' + resp['code'] + '</p>');
							if(resp['output'] != '')
							{
								$("#output").append('<pre>' + resp['output'] + '</pre>');
							}
							var scrollTop = $("#output")[0].scrollHeight;
							$("#output").scrollTop(scrollTop); 
						});
						return false; 
					} 
				});
			});
			</script>
			<body>
				<div id="output" scrolling="no">%s</div>

				<div id="input">
					<textarea class='prompt' style="width:50px" readonly>php&gt;&gt;</textarea>
					<textarea class='prompt' id="ip" style="width:487px"></textarea>
				</div>
				<p style="clear:both">Powered By Lee</p>
			</body>
		</html>
		"""
		html = templates%(uid,PHP_VERSION_INFO)
		self.write(html)
		return


class StatementHandler(tornado.web.RequestHandler):
	def get(self):
		uid = self.get_argument('u',0)
		if uid == 0 or not PHPSHELLS.has_key(uid):
			self.write("uid not exists,maybe connection timeout,please restart\n")
			return
		else:
			command = self.get_argument('c','')
			command = command.encode('utf-8')
			php = PHPSHELLS[uid]
			restart,code,output = php.input(command)
			
			final = {
					'code'	:	code,
					'output':	output,
					}
			if restart == True:
				final['output'] += "php restart\n"

			self.write(json.dumps(final))

			return

class FaviconHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("")
		return

application = tornado.web.Application([
	("/", IndexHandler),
	("/statement", StatementHandler),
	("/favicon.ico",FaviconHandler)
	])

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(8999)
tornado.ioloop.IOLoop.instance().start()

