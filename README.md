# stack-trace-classifier
A typical java stack trace exception might look something like the following

```	
com.google.net.rpc3.RpcException: PurchaseOrder notification to BILLABLE_SERVICE_GOOGLE_STORE_PURCHASE_ORDER_BUYER failed
APPLICATION_ERROR;moneta.integrator.callbacks.purchaseordernotification/GoogleStorePurchaseOrderNotificationService.NotifyPurchaseOrder;com.google.net.rpc3.client.RpcClientException: <eye3-ignored title='/SubscriptionDmService.HandlePurchaseOrderNotification, INTERNAL'/> APPLICATION_ERROR;smashberry.domain.subscription/SubscriptionDmService.HandlePurchaseOrderNotification;<eye3-ignored title='null, FAILED_PRECONDITION'/> com.google.apps.framework.request.CanonicalCodeException: Backend service had error Code: FAILED_PRECONDITION
com.google.apps.framework.request.StatusException: <eye3-ignored title='INTERNAL'/> generic::INTERNAL: <eye3-ignored title='null, FAILED_PRECONDITION'/> com.google.apps.framework.request.CanonicalCodeException: Backend service had error Code: FAILED_PRECONDITION
        at com.google.wireless.android.smashberry.boq.common.producers.StatusOr.get(StatusOr.java:117)
        at com.google.wireless.android.smashberry.boq.domain.subscription.service.stateprocessors.StatusOrState.get(StatusOrState.java:70)
        at com.google.wireless.android.smashberry.boq.domain.subscription.service.stateprocessors.ProcessStateProducerModule.produceResult(ProcessStateProducerModule.java:117)
        Suppressed: com.google.common.labs.concurrent.LabsFutures$11: GraphFuture{key=@com.google.wireless.android.smashberry.boq.domain.subscription.service.purchaseordernotificationhandlers.Annotations$PurchaseOrderNotificationHandlerResult java.lang.Void} failed: com.google.apps.framework.request.StatusException: <eye3-ignored title='INTERNAL'/> generic::INTERNAL: <eye3-ignored title='null, FAILED_PRECONDITION'/> com.google.apps.framework.request.CanonicalCodeException: Backend service had error Code: FAILED_PRECONDITION
                at com.google.apps.framework.producers.PresentImpl.get(PresentImpl.java:31)
                at com.google.apps.framework.producers.FutureCollectionsRefiner$ListBridgeProducer.produce(FutureCollectionsRefiner.java:281)
	...
```

Needless to say, this is quite verbose and for an engineer looking to quickly identify an error from an 200+ line enormous stack trace, this can be quite tedious task. 

While the error message above is quite verbose, in reality, it could be summarized with just a couple of words:
```
PurchaseOrder notification to BILLABLE_SERVICE_GOOGLE_STORE_PURCHASE_ORDER_BUYER failed APPLICATION_ERROR.
Backend service had error Code: FAILED_PRECONDITION.
```
The purpose of the Stack Trace Classifier is to simplify the task of parsing the stack trace by retrieving a short and concise human-readable message. In addition, Stack Trace Classifier is able to cluster a large number of error messages in an unsupervised way to aid any engineer looking to quickly diagnose and correct active errors as soon as possible.

## Installation and Usage 
Note that the current stack-trace-classifier is heavily attuned and configured for the Payments CES team, thus usage of this project outside of this purpose may require minor tweaks to the main file, most notably the method to which the dataframe is imported. The expected input to the classifier in its current form is a pandas dataframe table with rows denoting separate errors with columns containing information on the given error. It is expected that at least one of these columns is the stack trace exception for the error. This method is extensible to any API call that easily converts to pandas dataframes, for example bigquery has a single API call capable of converting any bigquery table into a pandas dataframe. An example of integration with bigquery is included in stack_trace_classifier_main.py. A similar method exists for plx (Internal google tool) table which can easily be converted to a pandas table with an API call.

Steps to run stack-trace classifier through integration with bigquery
Either natively through python3
1. Create a python virtual environment following the instructions on their [main website](https://docs.python.org/3/library/venv.html)
2. run ```pip3 -r requirements.txt```
3. run ```python3 stack_trace_classifier_main.py --config=config_file.textproto (--big_query_config=bq_config_file.textproto) ```

Alternatively, the project can also be built using bazel
1. Ensure bazel is installed from the [bazel page](https://bazel.build/)
2. run ```bazel build //python:stack-trace-classifier-main```
3. Navigate to bazel-bin. This is typically generated at the root of the workspace.
4. run ```./stack-trace-classifier-main --config=config_file.textproto (--bigquery_config=bq_config_file.textproto)```

Note: bazel currently has a strange issue with the google bigquery package installing its own version of six (1.12) even though bigquery requires six version 1.13+, a current work around is to simply delete the generated six directory (and keep the one generated by pip3).

## Sample Input and Outputs
The below samples are data gathered by from the errors collected on a daily basis by the Google Payments CES team. Although these files are shared as google sheets (csv), we are able to replicate the input and output through plx workflows.

[sample input 1](https://docs.google.com/spreadsheets/d/1NE3_mN8BDpxp8a69VM1tyNHLE3OSeeuRR8IuYNSjPsg/edit?usp=sharing)
[sample output 1](https://docs.google.com/spreadsheets/d/1kkY3JKJfH7bLpC2K1dVXuVuKnrdqQ4pJ6Du_RE5asiw/edit?usp=sharing)

[sample input 2](https://docs.google.com/spreadsheets/d/1AqR_ZngmdNDLoOOvMqeSzbX_Q06KlrOlh6YMaL_VYPk/edit?usp=sharing)
[sample output 2](https://docs.google.com/spreadsheets/d/1uRZ_IRcGh9MqvyRq4iAercbJp7W4-BjZbH4tXxen2m4/edit?usp=sharing)

In both of the above examples, we can see examples of how our classifier could be useful. Both sample inputs contain 50 or so java exceptions that can be quite a hassle to manually parse through. Using our classifier, we can quickly identify that there are approximately 5 different errors in both cases and quickly look for the root cause in the 'Text' field.

## Configuration Files
The main configuration file utilized by stack-trace classifier is a [protocol buffer](https://developers.google.com/protocol-buffers) located in proto/config.proto with a number of example configurations included. The primary purpose of the configuration file is to make the input sanitizing and tokenization as extensible as possible. Each field is annotated with comments describing its purpose and usage. To create your own configuration, create a new text proto file and ensure all required fields are inputted. 

To see in depth explanations of each configuration possible, please take a look at the [design doc](https://docs.google.com/document/d/1mwYsHOTWWXWZZA3yZG2AJ7de6fpS4waJsY0_4vDL4es/edit?usp=sharing). 

In addition to the main configuration, stack-trace-classifier also has a bigquery configuration protocol buffer that it utilizes for reading and writing to that can be utilized by a workflow. Please see the file proto/big_query_config.proto for more details.

## Classification Methodology
In this section, we give a slightly more in depth explanation of how our classifier works. 
1. Given our stack trace errors, we first pattern match to a specific set of 'already known' error codes. These error codes are extracted from the protobufs that define these errors in the first place. Eventually, these error codes are provided as an additional layer of information (if found).
2. Next, for each exception, we first process the stack trace to remove extraneous information. Examples of some of the filtering we do are as follows:
	* For an english readable classification, we remove any line that begins with '\tat' since java exception convention generates these lines that provide nothing human readable in the sense of trying to cluster errors. 
	* Similarly, we remove any line that begins with 'Suppressed:' since these are clearly java generated lines
3. Next, with our sanitized input, we attempt to tokenize using various rules. Below are some examples:
	* We perform a preemptive tokenize using new lines and spaces
	* We filter out all single character tokens as these are usually either punctuations or negligible words like 'a'
	* We split on '=' since often error messages contain embedded data types like 'id=1211124'
	* We remove all trailing and leading punctuation
	* We filter out all hex numerals and decimal numerals since these are often ip addresses, version numbers and processIds.
4. The tokenized errors are then converted to vectors using term frequency vectorization (read more about term frequency and its sibling, tf-idf [here](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)). Afterwards, we use K-Means clustering to group our vectors (read more about K-Means Clustering [here](https://en.wikipedia.org/wiki/K-means_clustering)). The metric we ultimately use for K-Means clustering is Cosine Similarity. We used Cosine Similarity rather than simply Euclidean distance since in practice, error messages often repeated themselves variable numbers of times. I.E. an error of the form ```Transaction id:1111 failed because of cancellation ... Transaction id:1111 failed because of cancellation``` should be appear in the same cluster as an error like ```Transaction id:1234 failed because of cancellation```