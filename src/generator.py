import os
import json
from dotenv import load_dotenv
load_dotenv()


GEMINI_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

try:
	from google import genai
	from google.genai import types
except Exception:
	genai = None
	types = None


if GEMINI_KEY and genai:
	try:
		gemini_client = genai.Client(api_key=GEMINI_KEY)
	except Exception:
		gemini_client = None
else:
	gemini_client = None


# We'll create a unified interface: generate_script(topic, length_minutes)


def generate_prompt(topic, minutes=7):
	return (
		f"You are producing a podcast script (Host + Guest). Topic: {topic}. "
		f"Length target: approximately {minutes} minutes of spoken audio. "
		"Structure: Intro (Host), Guest intro, 3 main points with short back-and-forth, and a closing. "
		"Write natural, conversational dialogue. Mark speaker lines like 'Host:' and 'Guest:'."
	)




def call_gemini(prompt):
	# Use the Google GenAI client (gemini) when available.
	if not gemini_client:
		return None

	try:
		response = gemini_client.models.generate_content(
			model='gemini-2.5-flash',
			contents=prompt,
		)
		text = response.text if hasattr(response, 'text') else str(response)
		return text if text else None
	except Exception as e:
		print('Gemini generation failed:', e)
		return None




def call_openai_fallback(prompt):
	try:
		import openai
		openai.api_key = OPENAI_KEY
		resp = openai.ChatCompletion.create(
			model='gpt-4o-mini',
			messages=[{'role':'user','content':prompt}],
			max_tokens=1500,
			temperature=0.7
		)
		return resp['choices'][0]['message']['content']
	except Exception as e:
		print('OpenAI fallback failed:', e)
		return None




def generate_script(topic, minutes=7):
	prompt = generate_prompt(topic, minutes)
	text = None
	text = call_gemini(prompt)
	if not text:
		text = call_openai_fallback(prompt)
	if not text:
		# very small local fallback
		text = f"Host: Welcome. Today we talk about {topic}. Guest: Thanks. Let's discuss the main points..."

	# Produce a simple title and description from the topic
	title = f"Daily Brief: {topic}"
	description = f"Automated briefing covering recent developments about: {topic}. Generated automatically."

	return {
		'title': title,
		'description': description,
		'script': text
	}


if __name__ == '__main__':
	print(generate_script('sample trending topic'))
