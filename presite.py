import os
import shutil
import markdown
import frontmatter
import datetime
import json
from jinja2 import Template
from pathlib import Path

class Generator:
  def __init__(self, content = "", dest_path = "output.html", config = {}, is_markdown = False):
    if not dest_path:
      raise ValueError('dest_path must have a value.')

    self.content = content
    self.dest_path = dest_path
    self.config = config
    self.dest_path_elements = self.dest_path.split(os.path.sep)
    self.dest_path_elements = list(filter(lambda x: x != '' and x != '.', self.dest_path_elements))
    self.is_markdown = is_markdown

  def generate(self, presite):
    parsed = frontmatter.loads(self.content)

    self.config.update(parsed)

    if self.is_markdown:
      parsed.content = markdown.markdown(parsed.content)

    template = Template(parsed.content)

    result = template.render(self.config)

    combined_config = self.config
    combined_config['content'] = result

    templatetxt = '{{content}}'

    if 'template' in combined_config:
      with open(presite.selected_template_folder() + combined_config['template'] + '.html') as f:
        templatetxt = f.read()

    template = Template(templatetxt)
    result = template.render(combined_config)

    currentdir = './'
    
    for dir in self.dest_path_elements[:-1]:
      currentdir = currentdir + dir + '/'
      if not os.path.exists(currentdir):
        os.mkdir(currentdir)

    with open(self.dest_path, 'w+') as f:
      f.write(result)
      print('wrote ' + self.dest_path)

class SourceFileGenerator(Generator):
  def __init__(self, source_path, dest_path, config):
    if not source_path or not os.path.exists(source_path):
      raise ValueError('source_path must exist.')

    text = ''

    with open(source_path) as f:
      text = f.read()

    is_markdown = False

    ext = os.path.splitext(source_path)[1].lower()

    if ext == '.md' or ext == '.markdown':
      is_markdown = True


    super().__init__(text, dest_path, config, is_markdown)

class DataLoader:
  def __init__(self):
    pass

  def load(self):
    raise NotImplementedError()

class Presite:
  def __init__(self):
    self.data_loaders = []
    self.build_config = {}
    self.global_config = {}
    pass

  def register_data_loader(self, loader):
    self.data_loaders.append(loader)
    pass

  def selected_template_folder(self):
    if 'selected_template' not in self.build_config or self.build_config['selected_template'] == '':
      return './templates/default/'

    return './templates/' + self.build_config['selected_template'] + '/'

  def begin_build(self):
    if not os.path.exists('data'):
      os.mkdir('./data')

    if not os.path.exists('pages'):
      os.mkdir('./pages')

    if not os.path.exists('posts'):
      os.mkdir('./posts')

    if not os.path.exists('templates'):
      os.mkdir('./templates')
      os.mkdir('./templates/default')

    if os.path.exists('./build_config.json'):
      with open('./build_config.json', 'r') as f:
        self.build_config = json.load(f)

    if os.path.exists('./global_config.json'):
      with open('./build_config.json', 'r') as f:
        self.global_config = json.load(f)

    if os.path.exists('./output'):
      shutil.rmtree('./output')

    os.mkdir('./output')
    os.mkdir('./output/site')

    template_folders = next(os.walk(self.selected_template_folder()))[1]

    for f in template_folders:
      shutil.copytree(self.selected_template_folder() + f, './output/site/' + f)

    self.global_config['posts'] = self.list_post_metadata()
    self.global_config['pages'] = self.list_page_metadata()

  def list_pages(self):
    return os.listdir('./pages')

  def list_page_metadata(self):
    metadata = []

    for p in self.list_pages():
      fm = frontmatter.load('./pages/' + p)
      ext = os.path.splitext(p)

      page = {
        "filename": p,
        "url": '/' + ext[0] + '.html',
        "title": fm['title'] if 'title' in fm else '',
        "template": fm['template'] if 'template' in fm else ''
      }

      metadata.append(page)

    return metadata

  def list_posts(self):
    return os.listdir('./posts')

  def list_post_metadata(self):
    metadata = []
    for p in self.list_posts():
      date = p[0:10].split('_')
      slug = p[11:]
      postdate = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
      ext = os.path.splitext(p)
      slugext = os.path.splitext(slug)

      fm = frontmatter.load('./posts/' + p)

      draft = False if ('status' in fm and fm['status'] == 'draft') or postdate < datetime.datetime.now() else 'published'

      post = {
        "filename": p,
        "slug": slug,
        "url": '/' + str(postdate.year) + '/' + str(postdate.month).rjust(2, '0') + '/' + str(postdate.day).rjust(2, '0') + '/' + slugext[0] + '.html',
        "publish_date": postdate,
        "title": fm['title'] if 'title' in fm else '',
        "template": fm['template'] if 'template' in fm else '',
        "status": 'draft' if draft else 'published'
      }

      metadata.append(post)

    return metadata

  def load_data(self):
    self.global_config['data'] = {}

    for data in os.listdir('./data'):
      ext = os.path.splitext(data)

      if ext[1] == '.json':
        print('Loading ./data/' + data)

        with open('./data/' + ext[0] + '.json', 'r') as f:
          self.global_config['data'][ext[0]] = json.load(f)
          

    for dl in self.data_loaders:
      print("Loading data for " + dl.name + '...')
      self.global_config['data'][dl.name] = dl.load()

  def end_build(self):
    pass

  def build_pages(self):
    pages = self.list_pages()

    for p in pages:
      #print('Processing page ' + p + '...')
      ext = os.path.splitext(p)
      
      sfg = SourceFileGenerator('./pages/' + p, './output/site/' + ext[0] + '.html', self.global_config)
      sfg.generate(self)

  def build_posts(self):
    for p in self.list_post_metadata():
      if p['publish_date'] <= datetime.datetime.now():
      
        outpath = './output/site' + p['url']
        self.global_config['publish_date'] = p['publish_date']

        sfg = SourceFileGenerator('./posts/' + p['filename'], outpath, self.global_config)
        sfg.generate(self)
      else:
        print('Skipped post ' + p['filename'] + '...')

  def run(self):
    self.begin_build()
    self.load_data()
    self.build_pages()
    self.build_posts()
    self.end_build()

if __name__ == '__main__':
  p = Presite()
  p.run()