#!/usr/bin/env python
import _PyV8

JSEngine = _PyV8.JSEngine

import unittest

class TestWrapper(unittest.TestCase):
    def setUp(self):
        self.engine = JSEngine()
        
    def tearDown(self):
        del self.engine        
        
    def testConverter(self):
        self.engine.eval("""
            var_i = 1;
            var_f = 1.0;
            var_s = "test";
            var_b = true;
        """)
        
        var_i = self.engine.context.var_i
        
        self.assert_(var_i)
        self.assertEquals(1, int(var_i))
        
        var_f = self.engine.context.var_f
        
        self.assert_(var_f)
        self.assertEquals(1.0, float(self.engine.context.var_f))
        
        var_s = self.engine.context.var_s
        self.assert_(var_s)
        self.assertEquals("test", str(self.engine.context.var_s))
        
        var_b = self.engine.context.var_b
        self.assert_(var_b)
        self.assert_(bool(var_b))

class TestEngine(unittest.TestCase):
    def testClassProperties(self):
        self.assertEquals("1.0.1", JSEngine.version)
        
    def testCompile(self):
        engine = JSEngine()
        
        try:
            s = engine.compile("1+2")
            
            self.assertEquals("1+2", s.source)
            self.assertEquals(3, int(s.run()))
        finally:
            del engine
            
    def testExec(self):
        engine = JSEngine()
        
        try:
            self.assertEquals(3, int(engine.eval("1+2")))
        finally:
            del engine
            
    def testGlobal(self):
        class Global(object):
            version = "1.0"
            
        engine = JSEngine(Global())
        
        try:
            # getter
            self.assertEquals(Global.version, str(engine.context.version))            
            self.assertEquals(Global.version, str(engine.eval("version")))
                        
            self.assertRaises(UserWarning, JSEngine.eval, engine, "nonexists")
            
            # setter
            self.assertEquals(2.0, float(engine.eval("version = 2.0")))
            
            self.assertEquals(2.0, float(engine.context.version))       
        finally:
            del engine
            
    def testThis(self):
        class GlobalNamespace(object): pass
        
        engine = JSEngine(GlobalNamespace())
        
        self.assertEquals("[object global]", str(engine.eval("this")))
            
        
if __name__ == '__main__':
    unittest.main()