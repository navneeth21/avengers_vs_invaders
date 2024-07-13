import os
from dataclasses import dataclass

from typing import List,Dict

@dataclass
class Country_HQ:
    country_name: str
    country_code: str
    aliens: str
    predators: str
    dd_monsters: str

    def __str__(self):
        return f"Country_HQ(country_name='{self.country_name}', country_code='{self.country_code}', aliens='{self.aliens}', predators='{self.predators}', dd_monsters='{self.dd_monsters}')"

@dataclass
class Contacts:
    hq_name: str
    invader: str
    attack: str
    defense: str
    heal: str

    def __str__(self):
        return f"Contacts(hq_name='{self.hq_name}',invader='{self.invader}', attack='{self.attack}', defense='{self.defense}', heal='{self.heal}')"

@dataclass
class CombinedInfo:
    #country_name: str
    country_code: str
    hq_name: str
    invader: str
    attack: str
    defense: str
    heal: str
    invader_type: str

    @classmethod
    def combine(cls, country: Country_HQ, contact: Contacts):
        invader_type = ''
        if country.aliens == contact.hq_name:
            invader_type = 'aliens'
        elif country.predators == contact.hq_name:
            invader_type = 'predators'
        elif country.dd_monsters == contact.hq_name:
            invader_type = 'dd_monsters'
        else:
            return None  # No match found

        return cls(
            country_name=country.country_name,
            country_code=country.country_code,
            hq_name=contact.hq_name,
            invader=contact.invader,
            attack=contact.attack,
            defense=contact.defense,
            heal=contact.heal,
            invader_type=invader_type
        )

def parse_contacts_from_file(file_path: str) -> List[Contacts]:
    contacts = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        hq_name = lines[0].split('\t')[0].strip()
        
        for line in lines[1:]:
            parts = line.strip().split('\t')
            contact = Contacts(
                hq_name=hq_name,
                invader=parts[0],
                attack=parts[1] if len(parts) > 1 else '',
                defense=parts[2] if len(parts) > 2 else '',
                heal=parts[3] if len(parts) > 3 else ''
            )
            contacts.append(contact)
    return contacts

def gather_all_contacts(folder_path: str) -> Dict[str, List[Contacts]]:
    all_contacts = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            contacts = parse_contacts_from_file(file_path)
            
            # Use the filename (without extension) as the key
            key = os.path.splitext(filename)[0]
            all_contacts[key] = contacts
    
    return all_contacts

class TextDataExtractor:
    @staticmethod
    def extract_members_to_dict(file_path):
        country_hq_dict = {}
        
        with open(file_path, 'r') as file:
            next(file)  # Skip the header line if it exists
            for line in file:
                fields = line.strip().split('\t')
                if len(fields) >= 5:
                    country_name = fields[0].strip()
                    country_hq_dict[country_name] = {
                        'country_code': fields[1].strip(),
                        'aliens': fields[2].strip(),
                        'predators': fields[3].strip(),
                        'dd_monsters': fields[4].strip()
                    }
        
        return country_hq_dict

# Usage
if __name__ == "__main__":
    country_hq_file_path = "Option2_Tab_Delimited_Text/country_hq.txt"
    extractor = TextDataExtractor()
    country_hq_dict = extractor.extract_members_to_dict(country_hq_file_path)

    

    # Print the extracted contacts
    '''for contact in contacts:
        print(contact)
'''
    contacts_folder_path = "Option2_Tab_Delimited_Text/contacts"
    all_contacts = gather_all_contacts(contacts_folder_path)

    # Print the gathered contacts
    for filename, contacts in all_contacts.items():
        print(f"\nContacts from {filename}:")
        for contact in contacts:
            print(contact)

    # Print the total number of files processed
    print(f"\nTotal files processed: {len(all_contacts)}")


    # Uncomment to print country_hq_dict
    # import json
    # print(json.dumps(country_hq_dict, indent=2))