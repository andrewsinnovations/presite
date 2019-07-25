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

Here are some standard web browser colors, which were loaded in from a JSON data file:

<div class="row">
{{#data.colors}}<div class="colorswatch" style="background-color:{{hex}};"><span class="text-colorswatch">{{name}}<br/>{{hex}}</span></div>
{{/data.colors}}
</div>

[Here is a link to another page.](sample2.html)
