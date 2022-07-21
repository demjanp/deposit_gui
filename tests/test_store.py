#!/usr/bin/env python

import pytest

import deposit

@pytest.fixture(scope='module')
def store():
	
	yield deposit.Store()

def test_add_object(store):
	
	obj_id1 = store.add_object()
	obj_id2 = store.add_object()
	obj_id3 = store.add_object()
	obj_id4 = store.add_object()
	
	assert sorted(list(store.objects())) == [obj_id1, obj_id2, obj_id3, obj_id4]

def test_delete_object(store):
	
	store.del_object(2)
	
	assert sorted(list(store.objects())) == [1, 3, 4]
	
	store.add_object()
	
	assert sorted(list(store.objects())) == [1, 2, 3, 4]

def test_add_class(store):
	
	store.add_class("Cls A")
	
	assert list(store.classes()) == ["Cls A"]

def test_delete_class(store):
	
	store.add_class("Cls B")
	store.del_class("Cls A")
	
	assert list(store.classes()) == ["Cls B"]

def test_add_member(store):
	
	store.add_member("Cls A", 1)
	store.add_member("Cls A", 2)
	store.add_member("Cls B", 3)
	store.add_member("Cls B", 4)
	
	assert sorted(list(store.get_members("Cls A"))) == [1,2]
	assert sorted(list(store.get_members("Cls B"))) == [3,4]

def test_add_subclass(store):
	
	store.add_subclass("Cls B", "Cls A")
	
	assert list(store.get_subclasses("Cls B")) == ["Cls A"]
	
	assert sorted(list(store.get_members("Cls B"))) == [1,2,3,4]
	
	store.del_subclass("Cls B", "Cls A")
	
	assert sorted(list(store.get_members("Cls B"))) == [3,4]

def test_add_relation(store):
	
	store.add_relation(1, 3, "A-B")
	store.add_relation(1, 4, "A-B")
	store.add_relation(2, 1, "A-A", weight = 0.123)
	
	assert sorted(list(store.get_object_relations(1))) == [(2, "~A-A"), (3, "A-B"), (4, "A-B")]
	assert store.get_relation_weight(2, 1, "A-A") == 0.123

def test_add_class_relation(store):
	
	store.add_class_relation("Cls A", "Cls B", "ClsA-B")
	
	assert sorted(list(store.get_class_relations("Cls A"))) == [('Cls B', 'ClsA-B')]
	assert sorted(list(store.get_all_relations("Cls A"))) == [('Cls A', 'A-A'), ('Cls B', 'A-B'), ('Cls B', 'ClsA-B')]
	
def test_add_descriptor(store):	
	
	store.add_descriptor(1, "Descr A1", 1)
	store.add_descriptor(1, "Descr A2", "X")
	store.add_descriptor(2, "Descr A1", 1.1)
	store.add_descriptor(3, "Descr B", {"value": 2})
	
	assert store.get_descriptor(1, "Descr A1") == 1
	assert store.get_descriptor(1, "Descr A2") == "X"
	assert store.get_descriptor(2, "Descr A1") == 1.1
	assert store.get_descriptor(3, "Descr B") == {"value": 2}
	assert sorted(list(store.get_object_descriptors(1))) == ['Descr A1', 'Descr A2']
	assert sorted(list(store.get_object_descriptors(2))) == ['Descr A1']
	assert sorted(list(store.get_object_descriptors(3))) == ['Descr B']
	assert sorted(list(store.get_all_descriptors("Cls A"))) == ['Descr A1', 'Descr A2']
	assert sorted(list(store.get_all_descriptors("Cls B"))) == ['Descr B']

def test_add_class_descriptor(store):
	
	store.add_class_descriptor("Cls A", "Descr C_A1")
	store.add_class_descriptor("Cls A", "Descr C_A2")
	store.add_class_descriptor("Cls B", "Descr C_B")
	
	assert sorted(list(store.get_class_descriptors("Cls A"))) == ['Descr C_A1', 'Descr C_A2']
	assert sorted(list(store.get_class_descriptors("Cls B"))) == ['Descr C_B']
	assert sorted(list(store.get_all_descriptors("Cls A"))) == ['Descr A1', 'Descr A2', 'Descr C_A1', 'Descr C_A2']
	assert sorted(list(store.get_all_descriptors("Cls B"))) == ['Descr B', 'Descr C_B']
	
def test_get_relations_to_class(store):
	
	assert sorted(list(store.get_relations_to_class(1, "Cls B"))) == [(3, 'A-B'), (4, 'A-B')]

def test_rename_class(store):
	
	store.rename_class("Cls A", "Cls A_")
	
	assert sorted(list(store.classes())) == ['Cls A_', 'Cls B', 'Descr A1', 'Descr A2', 'Descr B', 'Descr C_A1', 'Descr C_A2', 'Descr C_B']
	assert sorted(list(store.get_members("Cls A_"))) == [1,2]
	assert sorted(list(store.get_all_relations("Cls A_"))) == [('Cls A_', 'A-A'), ('Cls B', 'A-B'), ('Cls B', 'ClsA-B')]
	assert sorted(list(store.get_all_descriptors("Cls A_"))) == ['Descr A1', 'Descr A2', 'Descr C_A1', 'Descr C_A2']
	
	store.rename_class("Cls A_", "Cls A")

def test_set_relation_weight(store):
	
	store.set_relation_weight(1, 3, "A-B", 0.456)
	
	assert store.get_relation_weight(1, 3, "A-B") == 0.456
	
def test_del_member(store):
	
	store.del_member("Cls A", 1)
	
	assert sorted(list(store.get_members("Cls A"))) == [2]
	
	store.add_member("Cls A", 1)
	
def test_del_relation(store):
	
	store.del_relation(1, 3, "A-B")
	
	assert sorted(list(store.get_object_relations(1))) == [(2, "~A-A"), (4, "A-B")]
	
	store.add_relation(1, 3, "A-B")

def test_del_class_relation(store):
	
	store.del_class_relation("Cls A", "Cls B", "ClsA-B")
	
	assert sorted(list(store.get_all_relations("Cls A"))) == [('Cls A', 'A-A'), ('Cls B', 'A-B')]

def test_del_descriptor(store):
	
	store.del_descriptor(1, "Descr A1")
	
	assert store.get_descriptor(1, "Descr A1") == None
	assert store.get_descriptor(1, "Descr A2") == "X"
	
	store.add_descriptor(1, "Descr A1", 1)

def test_del_class_descriptor(store):
	
	store.del_class_descriptor("Cls A", "Descr C_A1")
	
	assert sorted(list(store.get_class_descriptors("Cls A"))) == ['Descr C_A2']
	assert sorted(list(store.get_all_descriptors("Cls A"))) == ['Descr A1', 'Descr A2', 'Descr C_A2']
	
	store.add_class_descriptor("Cls A", "Descr C_A1")

def test_get_connected(store):
	
	store.add_object() # 5
	store.add_object() # 6
	store.add_member("Cls C", 5)
	store.add_member("Cls C", 6)
	store.add_relation(3, 5, "B-C")
	store.add_relation(3, 6, "B-C")
	
	assert sorted(list(store.get_connected(1, "Cls C"))) == [
		[(1, 3, 'A-B'), (3, 5, 'B-C')], [(1, 3, 'A-B'), (3, 6, 'B-C')]
	]
	assert sorted(list(store.get_connected(2, "Cls C"))) == [
		[(2, 1, 'A-A'), (1, 3, 'A-B'), (3, 5, 'B-C')], 
		[(2, 1, 'A-A'), (1, 3, 'A-B'), (3, 6, 'B-C')]
	]
	assert sorted(list(store.get_connected(1, "Cls A"))) == [[(1, 2, '~A-A')]]
