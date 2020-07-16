#!/usr/bin/env python3
import platform
from pprint import pprint
import re
import shlex
import shutil
import sys
import time
import traceback

tty=shutil.get_terminal_size((80, 20))

if platform.system() == "Windows":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class Format_text(object):
	@staticmethod
	def color_dyn_function(color_name):
		def function_template(txt):
			return Format_text.color(color_name, txt)
		return function_template

	@staticmethod
	def emphasize_dyn_function(mark_name):
		def function_template(txt):
			return Format_text.mark(mark_name, txt)
		return function_template

	@staticmethod
	def log_dyn_function(bullet):
		def function_template(txt):
			return Format_text.log(text=txt, bullet=bullet)
		return function_template

	@staticmethod
	def get_style_info(style):
		if style in Format_text.get_colors() or style in Format_text.get_marks():
			if style in  Format_text.get_colors():
				style_type="color"
			else:
				style_type="mark"

			return dict(style=style, type=style_type)
		else:
			return None

	@staticmethod
	def get_style_formatted_words(
		chunks, 
		append=True,
		debug=False,
		format=True,
		index=None,
		pretags=[],
		posttags=[],
		words=[],
	):
		if debug is True:
			if append is True:
				pprint(chunks)
				print()
		for c, chunk in enumerate(chunks):
			if debug is True:
				print()
				print("chunk:", chunk)
			remain=None
			word=None
			if append is True:
				words.append(dict(
					word=None,
					end="",
					start="",
					space=" ",
					style=None,
					type=None,
				))
				word=words[-1]
			else:
				word=words[index]

			dy_rules=[
				dict(
					name="pretag",
					rule=r"^(?P<start>[^<]?)<(?P<style>.+?)>(?P<remain>.*)$",
				),
				dict(
					name="posttag",
					rule=r"^(?P<word_str>.*?)</(?P<style>.+?)>(?P<remain>.{3,})?(?P<end>[^>]?)$",
				)
			]
			
			matched_rule=False
			for dy in dy_rules:
				rule_name=dy["name"]
				reg_rule=re.match(dy["rule"], chunk)

				if reg_rule:
					style=reg_rule.group("style")
					dy_style_info=Format_text.get_style_info(style)
					if dy_style_info is not None:
						matched_rule=True
						word_str=None
						remain=reg_rule.group("remain")
						start=None
						end=None
						if rule_name == "pretag":
							start=reg_rule.group("start")
							if start:
								if debug is True:
									print("start:", start)
								if word["start"] == "":
									word["start"]=start
								else:
									print("Format_text start '{}' has already been set for '{}' with start '{}'".format(start, word["word"], word["start"]))
									sys.exit(1)

							word["style"]=dy_style_info["style"] 
							word["type"]=dy_style_info["type"]

							pretags.append(style)
						elif rule_name == "posttag":
							word_str=reg_rule.group("word_str")
							end=reg_rule.group("end")
							if debug is True:
								print("style", style)
							if end:
								if debug is True:
									print("end", end)
								if word["end"] == "":
									word["end"]=end
								else:
									print("Format_text end '{}' has already been set for '{}' with end '{}'".format(end, word["word"], word["end"]))
									sys.exit(1)	

							if word_str:
								if debug is True:
									print("word_str", word_str)
								if word["word"] is None:
									word["word"]=word_str
									word["style"]=dy_style_info["style"] 
									word["type"]=dy_style_info["type"] 
								else:
									print("Format_text word_str '{}' has already been set with word_str '{}'".format(word_str, word["word"]))
									sys.exit(1)	

							if not pretags:
								print("Format_text when closing tag '{}' no opening tag has been found".format(style))
								sys.exit(1)
							
							if style != pretags[-1]:
								print("Format_text when closing tag '{}' does not match opening tag '{}'".format(style, pretags[-1]))
								sys.exit(1)

							if debug is True:
								print("before pop:", pretags)
							pretags.pop()

						if remain:
							if debug is True:
								print("remain: '{}'".format(remain))
							rindex=None
							if index is None:
								rindex=c
							else:
								rindex=index

							Format_text.get_style_formatted_words(
								[remain],
								append=False,
								debug=debug,
								format=True,
								index=rindex,
								pretags=pretags,
								posttags=posttags,
								words=words,
							)
						
						break

			if matched_rule is False:
				if debug is True:
					print("not matched:", chunk)
				if word["word"] is None:
					word["word"]=chunk
					if pretags:
						tmp_style=pretags[-1]
						tmp_dy_style_info=Format_text.get_style_info(tmp_style)
						word["style"]=tmp_dy_style_info["style"]
						word["type"]=tmp_dy_style_info["type"]
				else:
					print("Format_text word_str '{}' has already been set with word_str '{}'".format(chunk, word["word"]))
					sys.exit(1)	

			if c != 0 and append is True:
				previous_word=words[c-1]
				if previous_word["style"] == word["style"]:
					if word["style"] is not None:
						if word["type"] == "mark":
							word["space"]=Format_text.mark(word["style"], " ")
						elif word["type"] == "color":
							word["space"]=Format_text.color(word["style"], " ")

		if append is True:
			if pretags:
				print("Format_text Error singleton opening tag(s) {}".format(pretags))
				sys.exit(1)
			if debug is True:
				pprint(words)

			return words

	@staticmethod
	def get_styled_word(word, word_info, format=True):
		tmp_word=word
		if format is False:
			return word
		if word_info["type"] == "mark":
			tmp_word=Format_text.mark(word_info["style"], word)
		elif word_info["type"] == "color":
			tmp_word=Format_text.color(word_info["style"], word)
		return tmp_word

	@staticmethod
	def wrap(
		text, 
		extra_space="",
		format=True,
		indent=None, 
		style=False,
		width="auto", 
	):
		if indent is None:
			indent=""
		else:
			indent=indent.replace("\t", "    ")

		indent+=extra_space

		if width is not None:
			if width != "auto":
				if not isinstance(width, int):
					print(Format_text.log(bullet="error", text="Format_text 'width' value '{}' not found. 'width' value must be in [None, int, 'auto']".format(width)))
					sys.exit(1)

		line_width=None
		if width is None:
			line_width=None
		else:
			if width == "auto":
				width=tty.columns
			line_width=width-len(indent)-len(extra_space)

			if line_width <= 0:
				return text

		words=[]
		if style is True:
			words_info=Format_text.get_style_formatted_words(
				text.split(), 
				append=True,
				format=format,
				index=None,
				pretags=[],
				posttags=[],
				words=[],	
			)

			for word_info in words_info:
				word="{}{}{}".format(word_info["start"], word_info["word"], word_info["end"])
				words.append(word)
		else:
			words=text.split()

		lines=[]
		line=[]
		line_styled=[]
		styles=[]
		tmp_text=""
		tmp_text_styled=""
		spaces=[]
		while words != []:
			previous=tmp_text
			previous_styled=None
			word_info=None
			if style is True:
				word_info=words_info[0]
				previous_styled=tmp_text_styled

			line.append(words[0])
			if style is True:
				if line_styled:
					spaces.append(word_info["space"])
				if word_info["style"] is None:
					line_styled.append(words[0])
				else:
					tmp_word=words[0]
					start_char=""
					if word_info["start"] != "":
						tmp_word=tmp_word[1:]
						start_char=word_info["start"]
					end_char=""
					if word_info["end"] != "":
						tmp_word=tmp_word[:-1]
						end_char=word_info["end"]
					tmp_word=Format_text.get_styled_word(tmp_word, words_info[0], format=format)
					line_styled.append("{}{}{}".format(start_char, tmp_word, end_char))

			tmp_text=" ".join(line)
			if style is True:
				tmp_text_styled=""
				for e, elem in enumerate(line_styled):
					if e == 0:
						tmp_text_styled=elem
					else:
						tmp_text_styled+="{}{}".format(spaces[e-1], elem)

			if line_width is not None and len(tmp_text) > line_width:
				if previous == "":
					words[0]=tmp_text[line_width:]
					if style is True:
						lines.append("{}{}".format(indent, Format_text.get_styled_word(tmp_text[:line_width], words_info[0], format=format)))
						line_styled=[]
						spaces=[]
						tmp_text_styled=""
					else:
						lines.append("{}{}".format(indent,tmp_text[:line_width]))

					line=[]
					tmp_text=""
				else:
					if style is True:
						lines.append(indent+previous_styled)
						line_styled=[]
						spaces=[]
						tmp_text_styled=""
					else:
						lines.append(indent+previous)
					
					line=[]
					tmp_text=""
			elif line_width is not None and len(tmp_text) == line_width:
				if style is True:
					lines.append(indent+tmp_text_styled)
					line_styled=[]
					spaces=[]
					tmp_text_styled=""
					words_info.pop(0)
				else:
					lines.append(indent+tmp_text)
				line=[]
				tmp_text=""
				words.pop(0)
				if line_width == 1:
					lines.append(" ")
			elif line_width is None or len(tmp_text) < line_width:
				if style is True:
					words_info.pop(0)
				words.pop(0)
				
				if words == []:
					if style is True:
						lines.append(indent+tmp_text_styled)
					else:
						lines.append(indent+tmp_text)
				
			time.sleep(.001)

		return "\n".join(lines)

	@staticmethod
	def get_tty_columns():
		return tty.columns

	@staticmethod
	def get_tty_lines():
		return tty.lines
	
	@staticmethod
	def clear_screen():
		print("\x1b[2J")
		print("\x1b[H")
	
	@staticmethod
	def clear_scrolling_history():
		print("\x1b[2J\x1b[H\x1b[3J", end="")

	@staticmethod
	def color(color_name, text):
		code1, code2 = Format_text.get_colors(color_name)
		return str("\x1b[{};{}m{}\x1b[0m".format(code1,code2,re.sub("(\\x1b\[\d;\dm|\\x1b\[\dm)", "", text)))

	@staticmethod
	def mark(mark_name, text):
		code = Format_text.get_marks(mark_name)
		return str("\x1b[{}m{}\x1b[0m".format(code,re.sub("(\\x1b\[\d;\dm|\\x1b\[\dm)", "", text)))

	@staticmethod
	def get_bullets(bullet=None):
		bullets=dict(
			error=Format_text.color("lred","\u00D7"),
			info=Format_text.color("cyan","#"),
			success=Format_text.color("lgreen","\u221A"),
			warning=Format_text.color("yellow","\u2206"),
		)
		if bullet is None:
			return bullets
		else:
			if bullet not in bullets:
				print(Format_text.error("bullet '{}' not found".format(bullet)))
				sys.exit(1)
			return bullets[bullet]

	@staticmethod
	def log(
		text="",
		bullet=None, # get_bullets to see choices
		indent=None,
		format=True, 
		style=False,
		width="auto",  # auto, int, None
	):
		if indent is None:
			indent=""
		else:
			indent=indent.replace("\t", "    ")

		if bullet is not None and bullet != "":
			if bullet in Format_text.get_bullets():
				bullet=Format_text.get_bullets(bullet)
				length_bullet=1
			else:
				words_info=Format_text.get_style_formatted_words(
					[bullet],
					append=True,
					format=format,
					index=None,
					pretags=[],
					posttags=[],
					words=[],		
				)
				bullet=Format_text.get_styled_word(words_info[0]["word"], words_info[0], format=format)
				length_bullet=len(words_info[0]["word"])

			indent+="{} ".format(" "*length_bullet)
		else:
			bullet=""

		reg_space=re.match(r"(\s*)?.*", text)
		extra_space=reg_space.group(1)

		text=Format_text.wrap(
			text, 
			extra_space=extra_space,
			format=format,
			indent=indent, 
			style=style,
			width=width,
		)

		if bullet is not None and bullet != "":
			position=len(indent)-length_bullet-1
			text="{}{}{}".format(position*" ", bullet+" ", text[len(indent):])
		return text
		
	@staticmethod
	def get_colors(color_name=None):
		colors={
			"black":[0,30],
			"blue":[0,34],
			"brown":[0,33],
			"cyan":[0,36],
			"dgray":[1,30],
			"green":[0,32],
			"lblue":[1,34],
			"lcyan":[1,36],
			"lgray":[0,37],
			"lgreen":[1,32],
			"lmagenta":[1,35],
			"lred":[1,31],
			"magenta":[0,35],
			"red":[0,31],
			"white":[1,37],
			"yellow":[1,33],
		}
		if color_name is None:
			return colors
		else:
			if color_name not in colors:
				print(Format_text.error("Color Name '{}' not found".format(color_name)))
				sys.exit(1)
			return colors[color_name]

	@staticmethod
	def get_marks(mark_name=None):
		marks={
			"bold": 1,
			"iverse": 7,
			"uline": 4,
		}
		if mark_name is None:
			return marks
		else:
			if mark_name not in marks:
				print(Format_text.error("Mark Name '{}' not found".format(mark_name)))
				sys.exit(1)
			return marks[mark_name]

	# the individual function are created here
	black=color_dyn_function.__func__("black")
	red=color_dyn_function.__func__("red")
	green=color_dyn_function.__func__("green")
	brown=color_dyn_function.__func__("brown")
	blue=color_dyn_function.__func__("blue")
	magenta=color_dyn_function.__func__("magenta")
	cyan=color_dyn_function.__func__("cyan")
	lgray=color_dyn_function.__func__("lgray")
	dgray=color_dyn_function.__func__("dgray")
	lred=color_dyn_function.__func__("lred")
	lgreen=color_dyn_function.__func__("lgreen")
	yellow=color_dyn_function.__func__("yellow")
	lblue=color_dyn_function.__func__("lblue")
	lmagenta=color_dyn_function.__func__("lmagenta")
	lcyan=color_dyn_function.__func__("lcyan")
	white=color_dyn_function.__func__("white")
	
	bold=emphasize_dyn_function.__func__("bold")
	uline=emphasize_dyn_function.__func__("uline")
	iverse=emphasize_dyn_function.__func__("iverse")

	error=log_dyn_function.__func__("error")
	info=log_dyn_function.__func__("info")
	success=log_dyn_function.__func__("success")
	warning=log_dyn_function.__func__("warning")
