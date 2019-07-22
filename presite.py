import os
import shutil
import markdown
import frontmatter
import chevron
import datetime
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

  def generate(self):
    parsed = frontmatter.loads(self.content)

    self.config.update(parsed)

    if self.is_markdown:
      parsed.content = markdown.markdown(parsed.content)

    result = chevron.render(parsed.content, self.config)

    combined_config = self.config
    combined_config['content'] = result

    #print(combined_config)

    template = '{{{content}}}'

    if 'template' in combined_config:
      #print('opening template' + combined_config['template'])
      with open('./templates/' + combined_config['template'] + '.html') as f:
        template = f.read()

    result = chevron.render(template, combined_config)

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
    self.data = {}
    pass

  def register_data_loader(self, loader):
    self.data_loaders.append(loader)
    pass

  def begin_build(self):
    if os.path.exists('./output'):
      shutil.rmtree('./output')

    os.mkdir('./output')
    os.mkdir('./output/site')

    template_folders = next(os.walk('./templates'))[1]

    for f in template_folders:
      shutil.copytree('./templates/' + f, './output/site/' + f)

  def list_pages(self):
    return os.listdir('./pages')

  def list_posts(self):
    return os.listdir('./posts')

  def load_data(self):
    for dl in self.data_loaders:
      self.data[dl.name] = dl.load()

  def end_build(self):
    pass

  def build_pages(self):
    pages = self.list_pages()

    for p in pages:
      print('Processing page ' + p + '...')
      ext = os.path.splitext(p)
      
      sfg = SourceFileGenerator('./pages/' + p, './output/site/' + ext[0] + '.html', {'data': self.data})
      sfg.generate()

  def build_posts(self):
    for p in self.list_posts():
      date = p[0:10].split('_')
      slug = p[11:]
      postdate = datetime.date(int(date[0]), int(date[1]), int(date[2]))

      if postdate <= datetime.date.today():
        print('Processing post ' + p + '...')
        ext = os.path.splitext(p)
        slugext = os.path.splitext(slug)
      
        outpath = './output/site/' + str(postdate.year) + '/' + str(postdate.month).rjust(2, '0') + '/' + str(postdate.day).rjust(2, '0') + '/' + slugext[0] + '.html'

        sfg = SourceFileGenerator('./posts/' + p, outpath, {'data': self.data})
        sfg.generate()
      else:
        print('Skipped post ' + p + '...')

  def run(self):
    self.begin_build()
    self.load_data()
    self.build_pages()
    self.build_posts()
    self.end_build()

class SampleDataLoader(DataLoader):
  def __init__(self):
    super().__init__()

    self.name = 'SampleDataLoader'

  def load(self):
    return {'test': 12345}

if __name__ == '__main__':
  p = Presite()
  p.register_data_loader(SampleDataLoader())
  p.run()