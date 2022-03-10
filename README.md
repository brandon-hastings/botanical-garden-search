# botanical-garden-search
 script to search botanical garden datasets hosted on gardenexplorer.org

I found myself needing to search through multiple botanical garden holdings after being given a massive list of plants. So I'll put this here in case anyone else finds themselves in this unique position.

This is by no means an exhaustive search of all botanical gardens, but they are major gardens in the US and Europe and it is a great place to start.

When calling the script, it takes two arguments: `project_folder` and `output_path`
Call using:
`garden-search.py /path/to/dataset/withplants.csv, path/to/output/folder/`

A text file with the results for each botanical garden will be created and stored in `output_folder` specified. Be aware that this script does take a few hours, but it is still better than a manual search.

The function to extract url links to each botanical garden site from gardenexplorer.org was adapted from [here](https://www.thepythoncode.com/article/extract-all-website-links-python). This has some useful tips on building web scrapers and is a great read if you're just starting out in web scraping like I was when I wrote this script.
