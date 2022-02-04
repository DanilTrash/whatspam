from database import Database

vcf_format = \
"""BEGIN:VCARD
VERSION:3.0
FN:+{}
N:+{};;;
item1.EMAIL;TYPE=INTERNET:danilawdt13@gmail.com
item1.X-ABLabel:Другое
item2.TEL:+{}
item2.X-ABLabel:Другое
CATEGORIES:40 000 WhatsApp,myContacts
END:VCARD
"""


def main():
    data = Database(288539576)
    user = data('user')[0]
    file_name = f'{user}.vcf'
    print(file_name)
    with open(file_name, 'w') as f:
        for number in data('number').dropna():
            print("'+" + number)
            f.write(vcf_format.format(
                number,
                number,
                number,
            ))


if __name__ == '__main__':
    main()
