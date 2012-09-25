# -*- coding:utf-8 -*
import subprocess
import select
import time
import os
import json

TAG_START = '#php_shell_start_lee_890707'
TAG_END = '#php_shell_end_lee_890707'
PHP = 'php -q -c /home/passport/webphpshell/php.ini phpshell.php'
PHP_VERSION_INFO = ''.join(os.popen('php -v').readlines())

class PHPShell():
	def __init__(self,timeout = 5):
		self.timeout = timeout
		self.p = subprocess.Popen(PHP,stdin = subprocess.PIPE,
				stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell = True)

	def input(self,command):
		self.p.stdin.write(command.strip())
		self.p.stdin.write("\n")
		self.p.stdin.flush()

		output = ''
		#first line == TAG_START
		op = self.p.stdout.readline().strip()
		
		assert(op == TAG_START)

		code = json.loads(self.p.stdout.readline().strip())[0]

		restart = False

		time_used = 0
		time_out = self.timeout
		interval = 0.1

		while True:
			readfds,writefds,errfds = select.select([self.p.stdout],[],[],0)

			"""
			if block
			"""
			if len(readfds) == 0:
				"""
				kill process if timeout
				"""
				if time_used > time_out:
					restart = True
					output = "connection timeout"
					break
				time_used += interval
				time.sleep(interval)
				continue
			else:
				op = readfds[0].readline().strip()
				retcode = self.p.poll()
				if retcode != None or op == "":
					restart = True
					break

				output = json.loads(op)[0]

				op = self.p.stdout.readline().strip()
				assert(op == TAG_END)
				break

		if restart:
			output += self.p.stderr.read()
			self.restart()

		return (restart,code,output)
				
	def restart(self):
		if self.p.poll() == None:
			self.p.kill()
		self.p = subprocess.Popen(PHP,stdin = subprocess.PIPE,
				stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell = True)
		return True

	def __del__(self):
		if self.p.poll() == None:
			self.p.kill()
		self.p = None

