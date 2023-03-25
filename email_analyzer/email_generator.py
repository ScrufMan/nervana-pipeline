def generate_emails(count, output_dir="sample_emails"):
    import random
    import os

    subjects = ["Reminder: Meeting Tomorrow", "Project Update", "Urgent Request", "Follow-up on Action Items",
                "Happy Holidays!", "New Product Announcement", "Invitation to Company Event", "Feedback Request",
                "Thank You"]
    eml_adress_pool = ["alice@example.com", "bob@example.com", "charlie@example.com", "david@example.com",
                  "emily@example.com", "frank@example.com", "grace@example.com", "henry@example.com",
                  "isabelle@example.com", "james@example.com", "matt@example.com", "clara@example.com"]

    # list of probabilities of number of recipients
    recipients_prob = [1,1,1,1,1,1,1,2,2,2,2,3,3,4]

    # Create the output directory if it doesn't already exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for i in range(count):
        # Choose a random subject, sender and recipient
        subject = random.choice(subjects)
        sender = random.choice(eml_adress_pool)

        n_recipients = random.choice(recipients_prob)
        recipients = []

        for _ in range(n_recipients):
            while (recipient := random.choice(eml_adress_pool)) in (recipients + [sender]):
                pass
            recipients.append(recipient)

        # Generate the email body
        body = f"Dear {recipients[0].split('@')[0]},\n\nI wanted to reach out to you regarding {subject.lower()}.\n\nBest regards,\n{sender.split('@')[0]}"

        # Generate the .eml filename
        filename = f"email_{i + 1}.eml"

        # Create the .eml file
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(f"To: {', '.join(recipients)}\n")
            f.write(f"From: {sender}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"\n{body}")

        print(f"Created {filename}")

    print("Done!")

if __name__ == '__main__':
    generate_emails(10)
