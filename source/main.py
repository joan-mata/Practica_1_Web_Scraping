from ev_scraper import EVDatabaseScraper

if __name__ == "__main__":
    scraper = EVDatabaseScraper()
    scraper.scrape(limit=None)
    scraper.data2csv("../dataset/ev_dataset.csv")