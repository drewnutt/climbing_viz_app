import os

files=['app.py','grades.py','figures.py','data_cleaning.py'] # files to be included in the index.html
requirements = ['plotly','requests'] # python packages to be installed
entrypoint = files[0] # entrypoint file, must be in the files list

# create gh_pages directory
os.makedirs('gh_pages', exist_ok=True)

with open('gh_pages/index.html', 'w') as f:
    header = '''
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />
    <title>Stlite app</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@0.80.1/build/style.css"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module">
import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.80.1/build/stlite.js"
mount(
  {
    requirements: ''' + str(requirements) + ''',
    entrypoint: "''' + entrypoint + '''",
    files: {
  '''
    f.write(header)
    for file in files:
        f.write(f'"{file}": `')
        if file == entrypoint:
            f.write("import micropip\nawait micropip.install('statsmodels')\n")
        with open(file, 'r') as g:
            f.write(g.read())
        f.write('`,\n')
    f.write('},\n    },\n    document.getElementById("root")\n  )\n</script>\n</body>\n</html>\n')

