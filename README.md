Overview
========
[![Build Status](https://travis-ci.org/felixonmars/suds-ng.svg?branch=master)](https://travis-ci.org/felixonmars/suds-ng)
suds-ng is a fork of [suds](https://fedorahosted.org/suds/).

TODO
====
- Fix existing issues
- Python 3 support

Support for overloaded methods
==============================

Although not recommended and explicitly disallowed in WSDL 1.2, some older implementations of SOAP servers provide
support for defining multiple methods with the same name and different number and/or types of arguments. 
Suds-ng provides basic support for interacting with these servers. 

While statically types languages can make use of types to determine which method is being called, there is no such 
option in Python.

Therefore, suds-ng provides multiple ways how to specify which overloaded method should be called.

**None of the changes have any impact on calling regular, non-overloaded methods.** 

#### Example methods
Suppose we have following methods defined in WSDL:

```python
Submit(xs:int sessionID, xs:string errorMessage, xs:string assetData)
Submit(xs:int sessionID, xs:int jobID, xs:boolean jobComplete, xs:string errorMessage, xs:string assetData)
Submit(xs:int SessionID, xs:int ApplianceID, xs:int JobID, xs:boolean JobComplete, xs:string ErrorMessage, xs:string Asset)
```
            

## Automatic selection

Automatic selection should cover most use cases of calling overloaded methods. It uses the same syntax as regular 
methods and uses parameter names to select the method.

There are the following limitations:
* Positional arguments are not allowed. Suds-ng uses parameter names to select the method so the names must be provided.
* All parameters that the respective overload accepts, must always be provided. This rule also applies to optional 
parameters. Note: Setting the parameter value to None will cause suds to only use the name for method selection, but not 
 include it in the actual SOAP request.
* It is not possible to differentiate between overloaded methods that accept the same parameter names, which 
only differ in type.

#### Examples

```python
# raises suds.OverloadedMethodWithPositionalArgumentsError
service.Submit(1, "message", "asset")  
# Correct invocation of the first method
service.Submit(sessionID=1, errorMessage="message", assetData="asset") 

# raises OverloadedMethodNotMatchingError, all parameters must be provided
service.Submit(SessionID=1, ApplianceID=2, JobID=3, JobComplete=False, Asset="asset")  
# Correct invocation fo the third method. 
# ErrorMessage is set to None, so it will not be sent in the request
service.Submit(SessionID=1, ApplianceID=2, JobID=3, JobComplete=False, ErrorMessage=None, Asset="asset") 
```

To overcome these limitations, suds-ng provides additional methods to assist with method selection.

## accepting_args
This method allows to specify one or more argument names which the method accepts. As opposed to automatic selection,
not all arguments are required (one unique name is often enough).

A partially or fully selected method is returned. If the argument(s) were unique just for a single method, 
the resulting method behaves like a non-overloaded one, therefore limitations from the previous paragraph no longer apply.

MethodNotFound is raised if no method accepts provided argument names.

#### Example
```python
# Correct invocations of the third method
service.Submit.accepting_args("ErrorMessage")(SessionID=1, ApplianceID=2, JobID=3, JobComplete=False, Asset="asset")
service.Submit.accepting_args("ErrorMessage")(1, 2, 3, False, "error message", "asset")
service.Submit.accepting_args("ErrorMessage", "JobID")(1, 2, 3, False, "error message", "asset")
```

## accepting_message, returning_message
These two methods allow to specify the input or output message name as is defined in WSDL.

MethodNotFound is raised if no such method is found.

#### Example
```python
# Both can be correct invocations of the first method if the messages are named so in WSDL.
service.Submit.accepting_message("SubmitRequest")(1, "message", "asset")
service.Submit.returning_message("SubmitResponse")(1, "message", "asset")
```

## List subscription
If everything else fails, it is possible to select the overloaded method by index.

This should be the least preferred option, as the order may unpredictably change.

```python
# Correct but not recommended invocation of the first method
service.Submit[0](1, "message", "asset")
```