#!/bin/bash
# test_all_pdfs.sh - Test all 8 legal PDFs with simple_rag.py
#
# Usage:
#   ./test_all_pdfs.sh              # Run tests and display output
#   ./test_all_pdfs.sh > results.txt   # Save output to file

echo "Testing all 8 legal PDFs..."
echo "======================================"
echo ""

echo "1. Immigration Case"
echo "-----------------------------------"
python simple_rag.py --pdf us_immigration_case.pdf --question "Why was the alien fiancé petition denied?"
echo ""

echo "2. Motion to Stay"
echo "-----------------------------------"
python simple_rag.py --pdf motion_to_stay.pdf --question "What did Victor George request from the court?"
echo ""

echo "3. Energy Supply & Demand"
echo "-----------------------------------"
python simple_rag.py --pdf energy_supply_demand.pdf --question "What was the trend in U.S. crude oil production from 2015 to 2017?"
echo ""

echo "4. Legal Case 2003"
echo "-----------------------------------"
python simple_rag.py --pdf a_2003-19.pdf --question "What statute or regulation is referenced in this document?"
echo ""

echo "5. Bank Evaluation"
echo "-----------------------------------"
python simple_rag.py --pdf barre_savings_bank_evaluation.pdf --question "What is the overall rating of this bank?"
echo ""

echo "6. Foreign Markets"
echo "-----------------------------------"
python simple_rag.py --pdf foreign_markets.pdf --question "What foreign markets are discussed in this document?"
echo ""

echo "7. Offshore Drilling Bill"
echo "-----------------------------------"
python simple_rag.py --pdf oc_bill_offshore_drilling.pdf --question "What is the main purpose of this bill?"
echo ""

echo "8. Subcommittee Charter"
echo "-----------------------------------"
python simple_rag.py --pdf ost_subcommittee_charter.pdf --question "What is the purpose of this subcommittee?"
echo ""

echo "======================================"
echo "All tests completed!"
