import os
import string
from random import choice
import json
from time import sleep

import lxml.html as HT
import requests
from logger import logger

# comment
LOGGER = logger('mailbox')


class Mailbox:
    def __init__(self, email_address=None):
        if email_address is None:
            mail_name, domain = None, None
        else:
            mail_name, domain = email_address.split('@')
        self.API = 'https://www.1secmail.com/api/v1/'
        self.s = requests.Session()

        if mail_name is None:
            self._mailbox = self._rand_pass()
        else:
            self._mailbox = mail_name  # change to your own test mailbox
        domains = [
            # '1secmail.com',
            # '1secmail.org',
            # '1secmail.net',
            'xojxe.com',
            'yoggm.com',
            'oosln.com',
            'vddaz.com'
        ]
        self._domain = domain or choice(domains)
        LOGGER.info(f'{self._mailbox}@{self._domain}')

    def __str__(self):
        return f'{self._mailbox}@{self._domain}'

    def _rand_pass(self):
        chars = string.ascii_letters + string.digits
        password = ''.join(choice(chars) for _ in range(9))
        return password

    def mailjobs(self, action, id=None):
        mail_list = 'error'
        act_ilst = ['getMessages', 'deleteMailbox', 'readMessage']
        act_dict = {
            'get': act_ilst[0],
            'del': act_ilst[1],
            'read': act_ilst[2]
        }
        if action in ['read', 'readMessage'] and id is None:
            print('Need message id for reading')
            return mail_list
        if action in act_dict:
            action = act_dict[action]
        elif action in act_ilst:
            pass
        else:
            print(f'Wrong action: {action}')
            return mail_list
        if action == 'readMessage':
            mail_list = self.s.get(self.API,
                                   params={'action': action,
                                           'login': self._mailbox,
                                           'domain': self._domain,
                                           'id': id
                                           }
                                   )
        if action == 'deleteMailbox':
            mail_list = self.s.post('https://www.1secmail.com/mailbox/',
                                    data={'action': action,
                                          'login': self._mailbox,
                                          'domain': self._domain
                                          }
                                    )
        if action == 'getMessages':
            mail_list = self.s.get(self.API,
                                   params={'action': action,
                                           'login': self._mailbox,
                                           'domain': self._domain
                                           }
                                   )
        return mail_list

    def filtred_mail(self, domain=True, subject=True, id=True, date=True):
        """Simpled mail filter, all params optional"""

        ma = self.mailjobs('get')
        out_mail = []
        if ma != 'error':
            list_ma = ma.json()
            for i in list_ma:
                if not id:
                    id_find = i['id'].find(id) != -1
                else:
                    id_find = id
                if not date:
                    dat_find = i['date'].find(date) != -1
                else:
                    dat_find = date
                if not domain:
                    dom_find = i['from'].lower().find(domain.lower()) != -1
                else:
                    dom_find = domain
                if not subject:
                    sub_find = i['subject'].lower().find(subject.lower()) != -1
                else:
                    sub_find = subject
                if sub_find and dom_find and id_find and dat_find:
                    out_mail.append(i['id'])

            if len(out_mail) > 0:
                return out_mail
            else:
                return 'not found'
        else:
            return ma

    def clear_box(self, domain, subject, clear=True):
        """Clear mail box if we find some message"""

        ma = self.filtred_mail(domain, subject)
        if isinstance(ma, list):
            ma = self.mailjobs('read', ma[0])
            if ma != 'error':
                if clear: print('clear mailbox')
                if clear: x = self.mailjobs('del')
                return ma
            else:
                return ma
        else:
            return ma

    def get_link(self, domain, subject, x_path='//a', clear=True):
        """Find link inside html mail body by x-path and return link"""

        ma = self.clear_box(domain, subject, clear)
        if ma != 'error' and ma != 'not found':
            mail_body = ma.json()['body']
        else:
            return ma
        web_body = HT.fromstring(mail_body)
        child = web_body.xpath(x_path)[0]
        return child.attrib['href']

    def check_last_mail(self):
        result = False
        while result is False:
            response = requests.get(self.API, params={'action': 'getMessages',
                                                 'login': self._mailbox,
                                                 'domain': self._domain})
            try:
                message = requests.get(self.API, params={'action': 'readMessage',
                                                    'login': self._mailbox,
                                                    'domain': self._domain,
                                                    'id': response.json()[0].get('id')})
            except IndexError as error:
                LOGGER.error(error)
                sleep(2)
            else:
                with open('message.html', 'w') as f:
                    f.write(message.json().get('body'))
                if 'message.html' in os.listdir(os.getcwd()):
                    result = True
                    return result


if __name__ == '__main__':
    mail = Mailbox('Daniltrashjob@esiix.com')
    print(mail.check_last_mail())
