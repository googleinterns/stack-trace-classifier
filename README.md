# stack-trace-classifier
Stack-Trace Classifier is a project that aims to shed additional light on stack-trace exception dumps. A classic exception might look something like

```	
com.google.moneta.api2.common.error.ApiException: <eye3-ignored title='moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ProxyChargeResponsePb.Error.ERROR_ORDER_NOT_CHARGED'/>  moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ProxyChargeResponsePb.Error.ERROR_ORDER_NOT_CHARGED
Underlying ApiErrors are: 
	moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ProxyChargeResponsePb.Error.ERROR_ORDER_NOT_CHARGED
	at com.google.moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ProxyChargeAction.execute(ProxyChargeAction.java:97)
	at com.google.moneta.purchaseorder.service.purchaseorder.purchaseorderinternal.ProxyChargeAction$$FastClassByCGLIB$$bd6cec39.invoke(<generated>)
	at com.google.apps.framework.inject.methodinvocation.DefaultMethodStateManager.invoke(DefaultMethodStateManager.java:20)
	at com.google.apps.framework.inject.MethodExecutor.execute(MethodExecutor.java:211)
	at com.google.apps.framework.request.impl.InterceptorInvocation.proceed(InterceptorInvocation.java:203)
	at com.google.moneta.api2.framework.common.ActionInvokerInterceptor$InvokeAppsFrameworkActionByReturningControlToAppsFramework.call(ActionInvokerInterceptor.java:58)
	at com.google.moneta.api2.framework.common.ActionInvokerInterceptor$InvokeAppsFrameworkActionByReturningControlToAppsFramework.call(ActionInvokerInterceptor.java:53)
    ...
```

Needless to say, this is quite verbose and for a engineer looking to quickly identify the error, can be quite daunting. 

The purpose of the Stack Trace Classifier is to simplify this task by parsing the stack trace and retrieving a human-readable message. Finally, Stack Trace Classifier clusters the error messages so as to avoid repetitive error messages.

Steps to run demo stack-trace Classifier

1. Create a python virtual environment https://docs.python.org/3/library/venv.html (recommended)
2. pip3 -r requirements.txt
3. python3 classifier.py

Example python demo output
```
                               COUNT
SERVER_UNEXPECTED_EXCEPTION     2952
SERVER_REMOTE_FRAMEWORK_ERROR     17
STORAGE_STALE_LOCK_TIMESTAMP       7
SERVER_PERSISTENCE_ERROR           5
STORAGE_DEADLINE_EXCEEDED          4
RPC.DEADLINE_EXCEEDED              1
                                                        COUNT
java.lang.IllegalArgumentException: No movement co...   1511
com.google.moneta.api2.common.error.ApiException:...    471
com.google.net.rpc3.client.RpcClientException: <ey...   21
com.google.net.rpc3.client.RpcClientException: <ey...   3
com.google.net.rpc3.client.RpcClientException: <ey...   3
com.google.net.rpc3.client.RpcClientException: <ey...   2
com.google.net.rpc3.client.RpcClientException: <ey...   1
java.lang.IllegalArgumentException: No movement co...   1
com.google.moneta.api2.common.error.ApiException:...    1
```

Note: The errors in the second half continue but are truncated but are indeed different errors.