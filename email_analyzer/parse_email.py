import email


def parse_email(eml_file):
    with open(eml_file, 'r') as f:
        msg = email.message_from_file(f)

        # Extract the email headers
        from_address = msg['From']
        to_address = msg['To']
        subject = msg['Subject']
        date_sent = msg['Date']

        # Extract the email body
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        # Return a dictionary with the extracted data
        return {'from': from_address, 'to': to_address, 'subject': subject, 'date_sent': date_sent, 'body': body}


# Example usage
# file = './files/mail1.eml'
# parsed_email = parse_email(file)
# print(parsed_email)
