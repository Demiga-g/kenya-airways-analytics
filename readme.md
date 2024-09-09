# Analyzing Passenger Reviews for Kenya Airways (KQ)

This is a web scrapping and data analytics project which provides an analysis of passenger reviews of the KQ airlines.
I have written an [article](https://medium.com/@midegageorge2/is-kenya-airways-really-the-pride-of-africa-022f868c804a) about the same.
Here is the snippet of the dashboard created in Power BI

![kq-ratings-reviews](https://github.com/user-attachments/assets/74b1b45d-810e-4a63-9ee9-0b9c269e06d0)

## Project's Files

- `extract_data.py`: This is a Python script for obtaining the required data.
- `kenya airways analytics.pbix`: A Microsoft PowerBI file containing the report and data models used to make the dashboard visualization.
- `kenya-airways-analytics.ipynb`: A Jupyter Notebook used for general data inspection.
- `requirements.txt`: A file with a list of the packages/libraries used for this project.

## Project's Requirements

- Python version 3.10.4
- A virtual environment (optional but advisable)
- Relevant packages

Here is the workflow of the project

![kq-review-scrapping](https://github.com/user-attachments/assets/1fe1cf55-53d3-44b7-ade0-a902cb63ee24)

For project reproducibility, you can run the following commands:

1. Clone this repository to your preferred folder

```bash
git clone https://github.com/Demiga-g/kenya-airways-analytics.git
```

2. (Optional) Set up and activate a virtual environment

```bash
python -m venv kq_analytics
source kq_analytics/bin/activate
```

3. Install the dependencies

```bash
pip install -r requirements.py
```

4. Run the web scrapping script. Note that this script has been configured to allow you scrap any airline review of your choice. In this case, we will use `kenya-airways`

```bash
mkdir -p data
python3 extract_data.py \
  --input_airline=kenya-airways \
  --input_page_size=200 \
  --input_sleep_time=3 \
  --output_data=data/kenya-airways.csv
```
What these commands do is:

- It starts by creating a directory `data`, if it does not exist, where the scrapped data will be stored.
- Runs the Python script with the name of the airline provided as indicated in the Skytrax website. Most of the time it will have a hyphen in between.
- Retrieve 200 reviews from a page then waits for three second before going to the next page.
- Stores the data in the `data` folder as a `.csv` file. Remember to append the `.csv` at the end of the name of the file.

Note: You may have to change the user agent accordingly.

5. (Optional) Visualization in Microsoft PowerBI

For this step, you can use your preferred visualization tool. However, should you decide to go with Microsoft PowerBI, note that there are some data cleaning steps you would have to take. These may include, but not limited:

- Splitting the `route` column to get the destination and origin columns
- Correctly naming the destination and origin countries (checking for spelling errors and abbreviated cities)
- Renaming the columns
- Replacing error values with `null`
- Creating calculated measures where necessary.
  
