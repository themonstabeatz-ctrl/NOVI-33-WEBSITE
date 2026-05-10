#!/bin/bash

# Skripta za postavljanje popusta za servise
# Koristi se kada promenite popust u booking sistemu

# Učitaj backend URL iz .env
BACKEND_URL="http://localhost:8001"

# Funkcija za postavljanje popusta
set_discount() {
    SERVICE_NAME=$1
    DISCOUNT=$2
    
    echo "Postavljam popust za '$SERVICE_NAME' na $DISCOUNT%..."
    
    curl -X POST "$BACKEND_URL/api/discount/set" \
      -H "Content-Type: application/json" \
      -d "{\"service_name\": \"$SERVICE_NAME\", \"discount_percentage\": $DISCOUNT}"
    
    echo ""
    echo "✅ Popust postavljen!"
}

# Provera argumenata
if [ $# -ne 2 ]; then
    echo "Upotreba: ./set_discount.sh \"Naziv servisa\" PROCENAT"
    echo ""
    echo "Primer:"
    echo "  ./set_discount.sh \"Masaža za parove\" 15"
    echo "  ./set_discount.sh \"Tradicionalna tajlandska masaža\" 10"
    echo "  ./set_discount.sh \"Masaža za parove\" 0  # Ukloni popust"
    exit 1
fi

set_discount "$1" "$2"
