/**
 * Web Research Agent - TypeScript Interface
 * Part of the Agentic RnD Tool multi-agent framework
 * 
 * This provides a TypeScript/JavaScript interface to the Python-based
 * web research agent for integration with Node.js applications.
 */

import { spawn } from 'child_process';
import * as path from 'path';

/**
 * Configuration for web research
 */
export interface ResearchConfig {
  maxSources?: number;
  depth?: number;
  timeout?: number;
  userAgent?: string;
  language?: string;
}

/**
 * Research result structure
 */
export interface ResearchResult {
  topic: string;
  timestamp: string;
  sources_found: number;
  sources_scraped: number;
  content: Array<{
    url: string;
    title: string;
    content: string;
    timestamp: string;
  }>;
  summary: string;
  failed_urls: Array<{
    url: string;
    error: string;
  }>;
}

/**
 * Web Research Agent class
 */
export class WebResearchAgent {
  private config: ResearchConfig;
  private pythonPath: string;
  
  constructor(config: ResearchConfig = {}) {
    this.config = {
      maxSources: 50,
      depth: 2,
      timeout: 300,
      userAgent: 'ResearchBot/1.0',
      language: 'en',
      ...config
    };
    
    // Path to Python script
    this.pythonPath = path.join(__dirname, 'scraper.py');
  }
  
  /**
   * Conduct research on a topic
   */
  async research(topic: string): Promise<ResearchResult> {
    return new Promise((resolve, reject) => {
      const args = ['python', this.pythonPath, topic];
      const process = spawn(args[0], args.slice(1));
      
      let stdout = '';
      let stderr = '';
      
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Research failed: ${stderr}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        }
      });
    });
  }
  
  /**
   * Scrape specific URLs
   */
  async scrapeUrls(urls: string[], extractLinks: boolean = false): Promise<any> {
    return new Promise((resolve, reject) => {
      const args = [
        'python',
        this.pythonPath,
        '--scrape',
        '--urls',
        urls.join(','),
        extractLinks ? '--extract-links' : ''
      ].filter(Boolean);
      
      const process = spawn(args[0], args.slice(1));
      
      let stdout = '';
      let stderr = '';
      
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Scraping failed: ${stderr}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        }
      });
    });
  }
}

/**
 * Factory function to create web research agent
 */
export function createWebResearchAgent(config?: ResearchConfig): WebResearchAgent {
  return new WebResearchAgent(config);
}

/**
 * Quick research function
 */
export async function research(topic: string, config?: ResearchConfig): Promise<ResearchResult> {
  const agent = new WebResearchAgent(config);
  return agent.research(topic);
}

export default {
  WebResearchAgent,
  createWebResearchAgent,
  research
};