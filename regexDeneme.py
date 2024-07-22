import spacy

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Example speech text
speech_text = """
We have a wedding on June 10, 2024. After that, we will celebrate Independence Day on July 4. 
Don't forget the Halloween party on October 31, and we will have a conference in December. We will also have Halloween Party, later.
"""

# Process the text with spaCy
doc = nlp(speech_text)

# Extract entities related to dates and events
for ent in doc.ents:
    if ent.label_ in ('DATE', 'EVENT'):
        print(ent.text, ent.label_)
