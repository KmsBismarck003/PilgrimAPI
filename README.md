# Laika Club - Pilgrim API Gateway

## Overview
This repository contains Pilgrim, the official API Gateway and core routing engine for the Laika Club ecosystem. Pilgrim serves as the central nervous system connecting all decoupled frontend applications to the backend microservices.

## Features
* Centralized request proxying and routing logic.
* Protocol translation and uniform interface exposure.
* Security enforcement, including Cross-Origin Resource Sharing (CORS) and authentication validation.
* Role-based access control and traffic management.

## Architecture
Pilgrim acts as a reverse proxy and abstraction layer. It isolates the Java-based microservices architecture from direct external access, ensuring that all communications from the Administrator, Manager, and Operator modules are standardized, logged, and secured.

## Usage
The API Gateway is intended to run as a core infrastructure component. Modifications to its routing tables or security middleware must adhere to strict internal deployment protocols.
