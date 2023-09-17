#!/usr/bin/env python3
#
# Simple ChatGPT Client
#
# Author: Matej Fabijanic <root4unix@gmail.com>
#

import click
import configparser
import getpass
import openai
import os
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from subprocess import call


config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['openai']['api_key']
model = config['openai']['model']
max_tokens = config['openai']['max_tokens']
temperature = config['openai']['temperature']
spinner = True

# Prompt the user for their API key if it hasn't been provided in
# the configuration already
openai.api_key = api_key
if api_key == "":
    openai.api_key = getpass.getpass(prompt="OpenAI API Key")

# Check the operating system and set the appropriate command to
# clear the terminal screen
if os.name == 'posix':
    clear = 'clear'
elif os.name == 'nt':
    clear = 'cls'

@click.group()
def main():
    """ Simple ChatGPT CLI"""
    pass

@click.command()
@click.option('-h', '--help')
def help():
    click.echo('Help test')

def loading_spinner(func):
    def wrapper(*args, **kwargs):
        text = TextColumn("[green]Requesting OpenAI...")
        with Progress(SpinnerColumn(), text,
        transient=True) as progress:
            progress.add_task("request")
            return func(*args, **kwargs)
    return wrapper

@loading_spinner
def generate_text(prompt):
    response = openai.Completion.create(
      model=model,
      prompt=prompt,
      max_tokens=int(max_tokens),
      temperature=float(temperature),
      top_p=1.0
    )
    return '>> %s' % response.choices[0].text.strip()

def clear_screen():
    _ = call('clear' if os.name == 'posix' else 'cls')
    click.echo("ChatGPT")

# Enter a while loop to continually prompt the user for input and
# generate responses from the OpenAI API
@main.command()
@click.option('-s', '--shell', is_flag=True,
help='interactive shell')
def shell(shell):
    click.echo("ChatGPT")
    while True:
        prompt = input('\n' + '> ')
        if prompt == 'quit' or prompt == 'exit':
            break
        elif prompt == "clear":
            clear_screen()
        elif prompt == "help":
            print('ChatGPT Cli - Help')
            print('  %s - clear screen' % 'clear' if os.name == 'posix' else 'cls')
            print('  exit - exit client')
            print('  quit - same as exit')
        else:
            try:
                text = generate_text(prompt)
            except openai.error.RateLimitError:
                print('ERROR: You exceeded your current quota, please check your plan and billing details.')
                print('       Check your API KEY "api_key" in config.ini under the section "\[openai]".')
                continue
            print(text)

if __name__ == '__main__':
    main()
