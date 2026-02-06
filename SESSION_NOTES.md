# Session Notes - AWS Infrastructure Setup

## 2025.02.01

### But first
- Attempted to have Claude create the Cloudformation for my end state goal first and then tests from that
- It went kind of nuts with the number of resources and it was very unweildy.
- Decided to start over and go step by step. 

### Behave Test Infrastructure
- Created `features/` directory structure with Behave BDD tests
- Created `features/environment.py` with setup/teardown hooks
- Created `features/steps/infrastructure_steps.py` with step definitions
- Added `requirements.txt` with behave and boto3 dependencies

### Makefile
- Created `Makefile` with `deploy`, `test`, `destroy`, and `all` targets

### VPC & Networking
- Created VPC (`blog-vpc`) with /24 CIDR block
- Created 4 subnets (/26 each): `public-a`, `public-b`, `private-a`, `private-b` across us-east-1a and us-east-1b
- Created Internet Gateway and attached it to the VPC
- Created public route table and associated it with public subnets
- Added default route (0.0.0.0/0) to the Internet Gateway

### EC2 Instance
- Created EC2 instance (`blog-instance`) with t3.micro, Amazon Linux 2023 AMI
- Created security group allowing SSH (port 22)
- Configured public IP assignment
- Attached SSH keypair (`jonny-personal-laptop`)

### Bug Fixes
- Fixed Amazon Linux AMI detection to recognize "al2023" naming convention
- Identified and fixed missing IGW route causing SSH timeout

### Usage
The week number includes some messing around I did earlier in the day as well. 

  Current session                                                                                                                                                                                
  ███████████████████▌                               39% used                                                                                                                                    
  Resets 11pm (America/New_York)                                                                                                                                                                 
                                                                                                                                                                                                 
  Current week (all models)                                                                                                                                                                      
  ████                                               8% used                                                                                                                                     
  Resets Feb 8 at 1pm (America/New_York)    


## 2025.02.05
                                                                                                                                                                                     
  - Planned a static site generator for jsywulak.com in a planning session, then implemented it                                                                                                  
  - Created build.py — globs content/*.md, parses YAML frontmatter via the markdown library's meta extension, renders posts through Jinja2 templates, writes HTML to site/, generates an index
  page (posts sorted newest-first) and a 404 page, copies static assets                                                                                                                          
  - Set up the content/template/static directory structure — content/ for markdown posts, templates/ for Jinja2 layouts (base.html for post pages, index.html for the post listing), static/ for
  CSS
  - Added styling (static/style.css) — Georgia serif font, 640px max-width container, minimal readable blog look
  - Wrote a first post (content/hello-world.md) with title/date frontmatter
  - Added jinja2 and markdown to requirements.txt alongside existing deps (behave, boto3, requests)
  - Updated the Makefile — added build target, wired deploy chain as deploy-website → build → deploy-content (S3 sync)
  - Gitignored site/ and deleted the old hand-maintained HTML files that build.py now generates
  - Updated CLAUDE.md to reflect the current state of the project — accurate project description, build/deploy commands, directory layout, how to add posts

### Usage

  Current session                                                                                                                                                                                
  ████████████████████████████████████▌              73% used                                                                                                                                    
  Resets 11pm (America/New_York)                                                                                                                                                                 

  Current week (all models)
  ████████                                           16% used
  Resets Feb 8 at 1pm (America/New_York)
