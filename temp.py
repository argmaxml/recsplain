# schema = T.MapType(T.StringType(), T.StringType())
schema = T.StructType(
    T.StructField("app", T.StructType( \
        T.StructField("ext", \
                      T.StructField('new_id', StringType(), True), \
                      T.StructField('sessionid', StringType(), True) \
                      , True), \
        T.StructField("storeurl", StringType(), True), \
        T.StructField("cat", ArrayType(LongType()), True), \
        T.StructField("name", StringType(), True), \
        T.StructField("id", StringType(), True), \
        T.StructField("publisher", \
                      T.StructField('domain', StringType(), True), \
                      T.StructField('name', StringType(), True), \
                      T.StructField("id", StringType(), True), \
                      T.StructField("bundle", StringType(), True) \
                      , True))), \
 \
    T.StructField("at", StringType(), True), \
    T.StructField(["bcat", StringType(), True]), \
    T.StructField("regs", T.StructType( \
        T.StructField("ext", \
                      T.StructField('gdpr', LongType(), True), \
                      T.StructField("coppa", LongType(), True)))), \
    T.StructField("source", T.StructType( \
        T.StructField("ext", \
                      T.StructField('omidpv', StringType(), True), \
                      T.StructField('omidpn', StringType(), True) \
                      , True)), \
                  T.StructField("pchain", StringType(), True), \
                  T.StructField("tid", StringType(), True), \
                  T.StructField("fd", LongType(), True)), \
    T.StructField("id", StringType(), True), \
    T.StructField("device", T.StructType( \
        T.StructField('os', StringType(), True), \
        T.StructField('ifa', StringType(), True), \
        T.StructField("h", LongType(), True), \
        T.StructField("js", LongType(), True), \
        T.StructField('Js', LongType(), True), \
        T.StructField("dnt", LongType(), True), \
        T.StructField("ua", StringType(), True), \
        T.StructField("devicetype", LongType(), True), \
        T.StructField("geo", \
                      T.StructField('zip', LongType(), True), \
                      T.StructField('country', StringType(), True), \
                      T.StructField('city', StringType(), True), \
                      T.StructField('metro', LongType(), True), \
                      T.StructField('lon', StringType(), True), \
                      T.StructField('type', StringType(), True), \
                      T.StructField('region', StringType(), True), \
                      T.StructField('lat', StringType(), True) \
                      , True), \
        T.StructField('pxratio', StringType(), True), \
        T.StructField('carrier', StringType(), True), \
        T.StructField("lmt", LongType(), True), \
        T.StructField("osv", LongType(), True), \
        T.StructField('Osv', LongType(), True), \
        T.StructField("w", LongType(), True), \
        T.StructField("model", StringType(), True), \
        T.StructField("connectiontype", StringType(), True), \
        T.StructField("make", StringType(), True)), \
                  T.StructField("imp", T.StructType( \
                      T.StructField('tagid', StringType(), True), \
                      T.StructField('displaymanager', StringType(), True), \
                      T.StructField("banner", \
                                    T.StructField('battr', [LongType(), True]), \
                                    T.StructField("w", LongType(), True), \
                                    T.StructField("h", StringType(), True), \
                                    T.StructField("api", [LongType(), True]), \
                                    T.StructField("mimes", ArrayType(StringType()), True), \
                                    True))), \
                                T.StructField('bidfloor', StringType(), True), \
                                T.StructField('bidfloorcur', StringType(), True), \
                                T.StructField('id', LongType(), True), \
                                T.StructField('secure', LongType(), True), \
                                T.StructField('exp', LongType(), True), \
                                T.StructField('instl', LongType(), True), \
                                T.StructField("user", StringType(), True), \
                                T.StructField("badv", StringType(), True)))
