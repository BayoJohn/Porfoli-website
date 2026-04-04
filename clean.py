import re
with open('app/templates/home.html', 'rb') as f:
    data = f.read()

# Decode ignoring errors
text = data.decode('utf-8', errors='ignore')
# Remove any remaining weird double line chars
text = re.sub(r'<!--[═\s]*[A-Z]+[═\s]*-->', '', text)

with open('app/templates/home.html', 'w', encoding='utf-8') as f:
    f.write(text)
