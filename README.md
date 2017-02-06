# Challenge

This project implements a chat application with python. In addition it is implemented with django as framework and channels to handle websockets and chatrooms.

## Implementation

I define 4 channels to handle the chat communication. Three of them are to initialize the websockets, to handle the messages and to disconnect. The other is a custom channel created to persist the data in the database as well as to consume the services from the URLs to get the financial data required.

In order to add the functionality to open different conversations with each person, I define a Room model with both users as subscribers, so each time a conversation is requested, it creates or opens the right channel.

Additionally, at the moment, we define two types of commands:

  *  /YQL|command=company
  *  /FNC|command=company
  
Both can set the parameters that I want to receive or the company from I want to get the data from. The prefix YQL is to get the information from the YQL yahoo service, and the FNC prefix is to get the information from the yahoo finance service.

As the YQL is like a query statement, I only support the **EQUAL** and the **IN** operation to filter the result. Most of the values could be initialized and changed like the **FROM** table, the **SELECT** statement and the **WHERE** filters. However if we try to retrieve non existing columns, we will have a message that the data is missing.

I am not using RabbitMQ for this solution, but it could be implemented aside the channels too. 

