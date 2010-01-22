class Parameter(models.Model):
    name = models.CharField(max_length=256,default="",blank=True)
    units = models.CharField(max_length=256,default="",blank=True)
    help_text = models.TextField(blank=True,default="")

    # for the actual value, we use a generic foreign key to
    # some data object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PostiveIntegerField()
    data = generic.GenericForeignKey('content_type','object_id')

    def as_python(self):
        return {self.name : self.data.as_python()}

    def children(self):
        return [sp.child for sp in SubParameter.objects.filter(parent=self)]

class SubParameter(models.Model):
    parent = models.ForeignKey(Parameter,related_name="parent")
    child = models.ForeignKey(Parameter,related_name="child")
    class Meta:
        order_with_respect_to = "parent"

class CaseParameterSet(models.Model):
    case = models.ForeignKey(Case)
    parameters = models.ForeignKey(Parameter) # reference to root parameter

class StringParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)
    value = models.TextField(blank=True,default="")
    display_name = "String Parameter"

    def as_python(self):
        return self.value

class IntegerParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)
    value = models.IntegerField()

    def as_python(self):
        return self.value

class DecimalParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)
    value = models.DecimalField()

    def as_python(self):
        return self.value

class ListParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)

    def param(self):
        return self.parameters.all()[0]

    def as_python(self):
        return [] # TODO

class DictionaryParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)

    def as_python(self):
        return dict() # TODO

class CurveParameter(models.Model):
    parameters = generic.GenericRelation(Parameter)

    def as_python(self):
        pass # TODO


class Output(models.Model):
    name = models.CharField(max_length=256,default="",blank=True)
    datatype = models.CharField(max_length=256,default="string",
                                choices=(("string","String"),
                                          ("integer","Integer"),
                                          ("float","Float"),
                                          ("list","List"),
                                          ("dictionary","Dictionary"),
                                          ("geo","Geospatial data"),
                                         ))
    value = models.TextField(blank=True,default="")

class SubOutput(models.Model):
    parent = models.ForeignKey(Output,related_name="parent")
    child = models.ForeignKey(Output,related_name="child")
    class Meta:
        order_with_respect_to = "parent"
    
class CaseOutput(models.Model):
    case = models.ForeignKey(Case)
    output = models.ForeignKey(Output) # root output

