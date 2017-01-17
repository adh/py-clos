#include <Python.h>

#define CACHE_NONE     '_'
#define CACHE_TYPE     'T'
#define CACHE_INSTANCE 'I'

typedef struct {
  PyObject* effective_method;
  size_t hash;
  PyObject* keys[]; 
} CacheEntry;

typedef struct {
  PyObject_HEAD
  char* cache_map;
  size_t specialized_count;
  size_t cache_size;
  CacheEntry** cache;
  int may_grow;
} GenericFunction;

static size_t hash_pointer(void* ptr){
  return (((size_t)ptr) * 13) ^ (((size_t)ptr) >> 12);
}

static size_t hash_combine(size_t a, size_t b){
  return (a * 17) + (b * 11);
}

static PyObject *
GenericFunction_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
    GenericFunction *self;

    self = (GenericFunction *)type->tp_alloc(type, 0);

    self->specialized_count = 0;
    self->cache_size = 0;
    self->cache_map = NULL;
    self->cache = NULL;
    
    return (PyObject *)self;
}

static int
GenericFunction_init(GenericFunction *self, PyObject *args, PyObject *kwds){
    return 0;
}

static PyObject* call_slow_path;
static PyObject* get_effective_method;

static void grow_cache(GenericFunction*self){
  size_t i;
  size_t j;
  size_t new_size = self->cache_size * 2;
  CacheEntry **new = malloc(sizeof(CacheEntry*) * new_size);
  
  for (i = 0; i < new_size; i++){
    new[i] = NULL;
  }

  for (i = 0; i < self->cache_size; i++){
    for (j = 0; j< new_size; j++){
      CacheEntry* e = self->cache[i];
      if (new[(e->hash + j)] == NULL){
        new[(e->hash + j)] = e;
        break;
      }
    }
  }

  for (i = 0; i < new_size; i++){
    if (new[i] == NULL){
      new[i] = malloc(sizeof(CacheEntry) +
                      sizeof(PyObject*) * self->specialized_count);
    }
  }

  free(self->cache);
  self->cache = new;
  self->cache_size = new_size;
}

static PyObject*
lookup_with_cache(GenericFunction *self, PyObject *args, PyObject *kwds){
  PyObject* keys[self->specialized_count];
  PyObject* em;
  size_t i;
  Py_ssize_t argcount = PyTuple_GET_SIZE(args);
  size_t hash = 0;
  CacheEntry* entry;
  
  if (argcount < self->specialized_count){
    PyErr_Format(PyExc_TypeError, "Function expects at least \%d arguments (got \%d)",
                 self->specialized_count, argcount);
  }
  
  for(i = 0; i < self->specialized_count; i++){
    PyObject* item = PyTuple_GET_ITEM(args, i);
    switch (self->cache_map[i]){
    case 'T':
      item = item->ob_type;
      break;
    case 'I':
      break;
    case '_':
      item = NULL;
    }
    keys[i] = item;
    hash = hash_combine(hash, hash_pointer(item));
  }

  hash = hash % self->cache_size;
  for (i = 0; i < self->cache_size; i++){
    entry = self->cache[(hash + i) % self->cache_size];
    
    if (entry->effective_method
        && entry->hash == hash
        && (memcmp(entry->keys, keys,
                   sizeof(PyObject*) * self->specialized_count) == 0)){
      return entry->effective_method;
    }

    if (!entry->effective_method){
      goto found_slot;
    }
  }
  if (self->may_grow){
    grow_cache(self);
    entry = self->cache[hash % self->cache_size];
    while (entry->effective_method){
      entry++;
    }
  } else {
    entry = self->cache[hash % self->cache_size];
  }
 found_slot:
  
  em = PyObject_CallMethodObjArgs(self,
                                  get_effective_method,
                                  args,
                                  NULL);

  if (em){
    entry->effective_method = em;
    entry->hash = hash;
    memcpy(entry->keys, keys, sizeof(PyObject*) * self->specialized_count);
  }
  
  return em;
}

static PyObject*
GenericFunction_call(GenericFunction *self, PyObject *args, PyObject *kwds){
  PyObject* em;
    
  if (!self->cache){
    return PyObject_CallMethodObjArgs(self, call_slow_path, args, kwds, NULL);
  }

  em = lookup_with_cache(self, args, kwds);
  if (!em){
    return NULL;
  }
  
  return PyObject_Call(em, args, kwds);
}

static void GenericFunction_dealloc(GenericFunction *self){
  size_t i;
  
  if (self->cache){
    for (i = 0; i < self->cache_size; i++){
      free(self->cache[i]);
    }
    free(self->cache);
  }
  
  if (self->cache_map){
    free(self->cache_map);
  }
  
}

static PyObject*
GenericFunction_initialize_cache(GenericFunction* self, PyObject* args){
  char* cache_map;
  size_t size;
  size_t i;
  int may_grow;
  

  if (!PyArg_ParseTuple(args, "ynp", &cache_map, &size, &may_grow)){
    return NULL;
  }

  if (self->cache){
    for (i = 0; i < self->cache_size; i++){
      free(self->cache[i]);
    }
    free(self->cache);
    self->cache = NULL;
  }

  self->specialized_count = strlen(cache_map);
  self->cache_map = strdup(cache_map);
  self->cache_size = size;
  self->may_grow = may_grow;
  
  if (self->cache_size){
    self->cache = malloc(sizeof(CacheEntry*) * self->cache_size);
    for (i = 0; i < self->cache_size; i++){
      self->cache[i] = malloc(sizeof(CacheEntry) +
                              sizeof(PyObject*) * self->specialized_count);
      self->cache[i]->effective_method = NULL;
    }
  }
  
  Py_RETURN_NONE;
}

static PyMethodDef GenericFunction_methods[] = {
  {"initialize_cache",
   (PyCFunction)GenericFunction_initialize_cache,
   METH_VARARGS,
   "Initialize C-level cache mechanism"
  },
  {NULL}  /* Sentinel */
};

static PyTypeObject GenericFunctionType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "py_clos._py_clos.GenericFunction",             /* tp_name */
    sizeof(GenericFunction), /* tp_basicsize */
    0,                         /* tp_itemsize */
    GenericFunction_dealloc,                         /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_reserved */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash  */
    GenericFunction_call,      /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "C implementation of generic function",   /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    GenericFunction_methods,             /* tp_methods */
    0, //GenericFunction_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)GenericFunction_init,      /* tp_init */
    0,                         /* tp_alloc */
    GenericFunction_new,                 /* tp_new */
};

static PyModuleDef py_closmodule = {
    PyModuleDef_HEAD_INIT,
    "_py_clos",
    "Caching implemented in C.",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__py_clos(void)
{
    PyObject* m;

    call_slow_path = PyUnicode_FromString("call_slow_path");
    get_effective_method = PyUnicode_FromString("get_effective_method");
    Py_INCREF(call_slow_path);
    
    if (PyType_Ready(&GenericFunctionType) < 0)
        return NULL;

    m = PyModule_Create(&py_closmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&GenericFunctionType);
    PyModule_AddObject(m, "GenericFunction", (PyObject *)&GenericFunctionType);
    return m;
}
