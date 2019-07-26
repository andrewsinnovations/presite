---
title: Hello World!
template: page
---

# Hello, world!

Welcome to a site generated with [Presite](https://www.github.com/andrewsinnovations/presite). 

Presite is a simple and flexible static site generator, written with Python3.

Presite supports pages and posts written in Markdown or in HTML:

* Item 1
* Item 2
* Item 3

# Posts

Presite, like most static site generators, has the concept of "posts." Here are some posts, ordered descending by date:

{% for p in posts|sort(attribute='publish_date', reverse=True) %}

- [{{p.title}}](./{{p.url}}) - {{p.publish_date.strftime("%m/%d/%Y")}}

{% endfor %}

# Loading in data

Here are some standard web browser colors, which were loaded in from a JSON data file in the data folder:

{% for color in data.colors %}
<div class="colorswatch" style="background-color:{{color.hex}};"><span class="text-colorswatch">{{color.name}}<br/>{{color.hex}}</span></div>
{% endfor %}

# How to use Presite

