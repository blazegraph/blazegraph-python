# blazegraph-python
Python client library for Blazegraph
(Pymantic fork)
========

Semantic Web and RDF library for Python

#Features Support Matrix

<table cellpadding="0" cellspacing="0">
	<colgroup>
		<col width="229">
		<col width="95">
	</colgroup>
	<colgroup>
		<col width="391">
	</colgroup>
	<colgroup>
		<col width="164">
	</colgroup>
	<tr>
		<td bgcolor="#ffffff" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0.02in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p align="center"><font color="#000000"><font face="Arial"><b>REST
			Endpoint</b></font></font></p>
		</td>
		<td colspan="2" bgcolor="#ffffff" style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0.02in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center"><font color="#000000"><font face="Arial"><b>Call
			/ parameters</b></font></font></p>
		</td>
		<td style="border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0.02in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center"><b>Pyton client (Pymantic)</b></p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in"></td>
	</tr>
	<tr>
		<td rowspan="13" bgcolor="#ffffff" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p align="left"><font color="#000000"><font face="Arial"><b>QUERY</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial">GET Request-URI
			?query=...</font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial">POST Request-URI
			?query=...</font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td rowspan="10" bgcolor="#ffffff" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="left"><font color="#000000"><font face="Arial"><b>parameters</b></font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>timestamp</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>explain</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>analytic</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>default-graph-uri</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>named-graph-uri</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>format</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>baseURI</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>includeInferred</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>timeout</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>${var}=Value</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><b>headers</b></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>X-BIGDATA-MAX-QUERY-MILLIS</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p><b>INSERT</b></p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>INSERT RDF (POST
			with Body)</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST Request-URI<br>...<br>Content-Type:<br>...<br>BODY</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>INSERT RDF (POST
			with URLs)</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial">POST Request-URI
			?uri=URI</font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p><b>DELETE</b></p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>DELETE with Query</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial">DELETE Request-URI
			?query=...</font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>DELETE with Body
			(using POST)</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST Request-URI ?delete<br>...<br>Content-Type<br>...<br>BODY</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p><b>UPDATE</b></p>
		</td>
	</tr>
	<tr>
		<td rowspan="3" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>UPDATE <br>(SPARQL
			1.1 UPDATE)</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST Request-URI ?update=...</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td rowspan="2" bgcolor="#ffffff" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="left"><font color="#000000"><font face="Arial"><b>parameters</b></font></font></p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>using-graph-uri</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial">using-named-graph-uri </font></font>
			</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">+</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>UPDATE (DELETE + INSERT)<br>(DELETE statements <br>selected
			by a QUERY plus <br>INSERT statements from <br>Request Body using
			PUT)</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>PUT Request-URI ?query=...<br>...<br>Content-Type<br>...<br>BODY</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>UPDATE <br>(POST
			with Multi-Part <br>Request Body)</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST Request-URI ?updatePost<br>...<br>Content-Type:
			multipart/form-data; boundary=...<br>...<br>form-data;
			name=&quot;remove&quot;<br>Content-Type:
			...<br>Content-Body<br>...<br>form-data; name=&quot;add&quot;<br>Content-Type:
			...<br>Content-Body<br>...<br>BODY</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p><b>Multi-Tenancy API</b></p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>DESCRIBE DATA SETS</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET /bigdata/namespace</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>CREATE DATA SET</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/namespace<br>...<br>Content-Type<br>...<br>BODY</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>DESTROY DATA SET</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>DELETE /bigdata/namespace/NAMESPACE</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>Transaction Management API</b></p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in"></td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx =&gt; txId</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>COMMIT-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx/txid?COMMIT</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>LIST-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET /bigdata/tx</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>CREATE-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx(?timestamp=TIMESTAMP)</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>STATUS-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx/txId?STATUS</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>ABORT-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx/txId?ABORT</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>PREPARE-TX</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/tx/txId?PREPARE</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in">
			<p><b>Access Path Operations</b></p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>FAST RANGE COUNTS</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET Request-URI
			?ESTCARD&amp;([s|p|o|c]=(uri|literal))[&amp;exact=(true|false)+</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>HASSTMT</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET Request-URI
			?HASSTMT&amp;([s|p|o|c]=(uri|literal))[&amp;includeInferred=(true|false)+</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td rowspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>GETSTMTS</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET Request-URI ?GETSTMTS<br>...<br>Content-Type<br>...</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST Request-URI ?GETSTMTS<br>...<br>Content-Type<br>…</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><font color="#000000"><font face="Arial"><b>DELETE with Access
			Path</b></font></font></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>DELETE Request-URI ?([s|p|o|c]=(uri|literal))+</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td colspan="4" bgcolor="#d9d2e9" style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0in"></td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>STATUS</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>GET /status</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
	<tr>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.03in; padding-right: 0.03in">
			<p><b>CANCEL</b></p>
		</td>
		<td colspan="2" style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p>POST /bigdata/sparql/?cancelQuery&amp;queryId=....</p>
		</td>
		<td style="border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0in; padding-right: 0.03in">
			<p align="center">-</p>
		</td>
	</tr>
</table>

Quick Start
-----------
```python
from pymantic import sparql

server = sparql.SPARQLServer('http://127.0.0.1:9999/bigdata/sparql')

# Loading data to Blazegraph
server.update('load <file:///tmp/data.n3>')

# Executing query
result = server.query('select * where { <http://blazegraph.com/blazegraph> ?p ?o }')
for b in result['results']['bindings']:
    print "%s %s" (b['p']['value'], b['o']['value']
```

Requirements
------------

Pymantic requires Python 2.6 or higher. Lepl is used for the Turtle and NTriples parser. httplib2 is used for HTTP 
requests and the SPARQL client. simplejson and lxml are required by the SPARQL client as well.


Install
------

```
$ python setup.py install
```

This will install Pymantic and all its dependencies.


Documentation
=============

Generating a local copy of the documentation requires Sphinx:

```
$ easy_install Sphinx
```

