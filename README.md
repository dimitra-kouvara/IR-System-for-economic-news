# IR-System-for-economic-news
An IR System based on Economic News using Bert Embeddings

Information Retrieval (IR) systems are widely used in attempt to obtain information relative to a query, from collections of various resources. There are numerous applications and implementations of such systems along with interesting research conducted in recent years. We present an IR system based on the recent breakthrough of Bert Embeddings. In this framework, Bert Embeddings are used to encode economic articles in 768 dense vector space, which serve as the basis of all computations and calculations conducted by the IR system.

Our approach is using crawlers to get the data from online economic sites and store them in a database. All articles are turned into Bert Embeddings and used to calculate similarities among them and queries, to extract common ground or context among them. The system offers access to the user through a Graphical User Interface (GUI), which presents the results collected from the IR ranked from the most relevant to the less relevant. Finally, instead of printing the whole article, the IR system provides summarized text output, created from another Bert Embeddings application, the text summarization.

To evaluate the results, an experiment of random words from random texts in the database was conducted, comparing whether the context of the random texts matches that of the extracted documents. Also, some user evaluation experiments were conducted, by assessing the results printed from a user perspective.
