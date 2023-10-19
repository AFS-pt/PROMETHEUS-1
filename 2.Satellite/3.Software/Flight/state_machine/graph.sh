export PYTHONDONTWRITEBYTECODE=1
cp buildtools/chart.py build/
cd build
python3 chart.py
dot -Tsvg graph.dot > ../output/state_machine.svg
convert -density 600 ../output/state_machine.svg ../output/state_machine.png
rm chart.py
rm graph.dot

# extraneous file removal
find . -type d -name __pycache__ -exec rm -r {} \+
cd - 
