"""Optional real-browser integration: install Playwright and its Chromium first.
Run: python -m unittest discover -s tests -p browser_labs.py -v
"""
import os
import shutil
import unittest
from playwright.sync_api import sync_playwright
from labs.support import json_service
from labs.web import serve_lab
from labs.stored_xss.attack import PAYLOAD

class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        cls.browser = cls.playwright.chromium.launch(executable_path=executable, headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    def context(self):
        context = self.browser.new_context()
        self.addCleanup(context.close)
        return context
    def test_stored_xss_executes_only_in_vulnerable_application(self):
        for vulnerable in (True, False):
            with self.subTest(vulnerable=vulnerable), serve_lab(vulnerable=vulnerable) as (_, origin):
                context = self.context()
                self.assertEqual(context.request.post(origin+'/api/login', data={'user':'alice','password':'dummy-correct-horse'}).status, 200)
                self.assertEqual(context.request.post(origin+'/api/comments', data={'body':PAYLOAD}).status, 201)
                page = context.new_page()
                page.goto(origin+'/comments')
                executed = page.evaluate('window.__pipelineproof_xss === 1')
                self.assertEqual(executed, vulnerable)
                self.assertIn('<script>', page.locator('article').inner_text() if not vulnerable else PAYLOAD)
                page.close()
    def test_credentialed_cors_read_only_in_vulnerable_application(self):
        with json_service({'/': {'page': 'synthetic attacker origin'}}) as (attacker, _):
            for vulnerable in (True, False):
                with self.subTest(vulnerable=vulnerable), serve_lab(vulnerable=vulnerable) as (_, origin):
                    context = self.context()
                    self.assertEqual(context.request.post(origin+'/api/login', data={'user':'alice','password':'dummy-correct-horse'}).status, 200)
                    page = context.new_page()
                    page.goto(attacker)
                    result = page.evaluate("""async (url) => {
                        try {
                            const response = await fetch(url, {credentials:'include'});
                            return {read:response.ok, body:await response.json()};
                        } catch (error) { return {read:false}; }
                    }""", origin+'/api/profile')
                    self.assertEqual(result['read'], vulnerable)
                    if vulnerable: self.assertEqual(result['body']['display_name'], 'Alice')
                    page.close()
