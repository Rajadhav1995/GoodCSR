from django.db import models
# Model managers for masterdate models


class ActiveQuerySet(models.QuerySet):

    def active_items(self):
        # Returns active items only
        return self.filter(active=2)

    def get_or_none(self, *args, **kwargs):
        # Returns object and return none if it's not present
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def filter_if(self, *args, **kwargs):
        for i in [i for i in kwargs if not kwargs.get(i)]:
            kwargs.pop(i)
        return super(ActiveQuerySet, self).filter(*args, **kwargs)

    def one(self, *args, **kwargs):
        # Returns one of the objects
        # Usefull while using shell
        try:
            return self.filter(*args, **kwargs).order_by('pk')[0]
        except:
            return None

    def latest_one(self, *args, **kwargs):
        # Returns one of the objects
        # Usefull while using shell
        try:
            return self.filter(*args, **kwargs).order_by('-id')[0]
        except:
            return None

    def __repr__(self):
        # Makes it easy to distinguish between qs and list
        return "#%s#" % (super(ActiveQuerySet, self).__repr__())

    def ids(self):
        # returns list of ids
        return [i.id for i in self]

    def vals(self, key, tipe={}):
        if tipe == {}:
            return set(self.values_list(key, flat=True))
        elif tipe == []:
            return self.values_list(key, flat=True)

    def each(self, save=False, func=None):
        if hasattr(save, '__call__'):
            func = save
            save = False
        for obj in self:
            func(obj)
            if save:
                obj.save()

    def sigma(self, attr):
        return self.aggregate(x=models.Sum(attr))['x'] or 0

    def draw(self, fields=None, display=30):
        from texttable import Texttable
        display = min(display, self.count())
        if not fields:
            fields = [i.name
                      for i in self.model._meta.fields
                      if i.name not in ['created', 'modified']]
        t = Texttable()
        t.add_rows([fields] + [
            [getattr(i, j) for j in fields]
            for i in self[:display]
        ])
        return "\nDisplaying {no} of {total} {model}s\n".format(
            no=display, total=self.count(), model=self.model.__name__
        ) + '-' * 40 + '\n' + t.draw()

    def export(self, fields=None):
        import csv
        if not fields:
            fields = [i.name
                      for i in self.model._meta.fields]
        file_name = '/tmp/%s.csv' % (str(self.model).replace('.', '_'))
        file_obj = open(file_name, 'wb')
        writer_obj = csv.writer(file_obj)
        writer_obj.writerow(fields)
        for i in self:
            writer_obj.writerow([getattr(i, j) for j in fields])
        file_obj.close()
