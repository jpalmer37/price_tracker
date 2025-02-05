from database import add_price_snapshot, get_latest_snapshots, list_snapshots

add_price_snapshot("99999", "Costco", "Zavida Organica Dark Coffee, 2 x 907 g", 46.99)
add_price_snapshot("1111111", "Costco", "LEANFIT Whey Protein – Vanilla Flavour", 59.99)
list_snapshots()