#!/usr/bin/env bash

debug_flag=""

metadata_config=config-metadata.txt

color_tty=""
color_tty="--color=tty"

echo ""
python validate_article.py ${debug_flag} -f test_data/test_file_001.md -s ${metadata_config} ${color_tty}


echo "================================================================================"
echo ""
python validate_article.py ${debug_flag} -f test_data/test_file_002.md -s ${metadata_config} ${color_tty}


echo "================================================================================"
echo ""
python validate_article.py ${debug_flag} -f test_data/test_file_003.md -s ${metadata_config} ${color_tty}


echo "================================================================================"
echo ""
python validate_article.py ${debug_flag} -f test_data/test_file_004.md -s ${metadata_config} ${color_tty}


echo "================================================================================"
echo ""
python validate_article.py ${debug_flag} -f test_data/test_file_005.md -s ${metadata_config} ${color_tty}

