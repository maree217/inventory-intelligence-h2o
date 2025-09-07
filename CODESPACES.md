# 🚀 GitHub Codespaces Deployment Guide

## 📋 Quick Start for Client Demos

### Option 1: One-Click Demo Launch
1. Click [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/yourusername/inventory-intelligence-h2o?quickstart=1)
2. Wait 2-3 minutes for environment setup
3. Run: `./scripts/codespaces-demo.sh`
4. Access dashboard at the provided URL

### Option 2: Manual Setup
```bash
# In your Codespace terminal
./scripts/codespaces-demo.sh
```

## 💰 Cost Optimization Strategy

### Resource Usage (Based on GitHub Free Tier: 120 core-hours/month)

| Demo Duration | CPU Hours Used | Demos per Month* |
|---------------|----------------|------------------|
| **30 minutes** | 1 hour | 120 demos |
| **1 hour** | 2 hours | 60 demos |  
| **2 hours** | 4 hours | 30 demos |
| **4 hours** | 8 hours | 15 demos |

*Assumes 2-core Codespace (default)

### Smart Usage Tips

#### ⚡ **On-Demand Strategy** (Recommended for Client Demos)
- **Before Demo**: Start Codespace 5 minutes early
- **During Demo**: Present live dashboard and H2O cluster
- **After Demo**: Run `./scripts/stop-demo.sh` immediately
- **Result**: ~1-2 core hours per client presentation

#### 🔄 **Auto-Suspend Settings**
- Codespaces auto-suspend after 30 minutes of inactivity
- You only pay for active compute time
- Suspended Codespaces don't consume CPU hours

#### 📊 **Demo Configurations**

**Quick Demo (30 min presentation)**
```bash
export DEMO_MODE=lightweight
./scripts/codespaces-demo.sh
```
- 2GB RAM limit for H2O
- 20 products instead of 50
- Streamlined UI
- **Usage**: ~1 core hour

**Full Demo (1-2 hour deep dive)**  
```bash
export DEMO_MODE=full
./scripts/codespaces-demo.sh
```
- 4GB RAM for H2O
- 50 products with full features
- Complete AutoML training
- **Usage**: ~2-4 core hours

## 🎯 Business Demo Script

### Opening (2 minutes)
1. **Problem Statement**: Show retail loss statistics
2. **Solution Overview**: H2O.AI advantage explanation
3. **Live Demo Promise**: "Let me show you this in action"

### Core Demo (20-25 minutes)
1. **Dashboard Overview** (5 min)
   - KPIs and business metrics
   - Point out 92% forecast accuracy vs 45% traditional

2. **AI Predictions** (8 min)  
   - Show real-time demand forecasting
   - Demonstrate reorder recommendations
   - Explain stockout risk alerts

3. **Advanced Analytics** (7 min)
   - ABC analysis for product categories
   - Seasonal trend detection
   - ROI optimization insights

4. **Technical Differentiation** (5 min)
   - H2O AutoML vs traditional methods
   - MOJO deployment benefits  
   - Native synthetic data generation

### Closing (3 minutes)
1. **Implementation Roadmap**: Week 1 to production
2. **ROI Projection**: Specific $ savings for their business
3. **Next Steps**: Pilot program proposal

## 🔧 Technical Setup Details

### Codespace Configuration
- **Machine Type**: 2-core, 8GB RAM (default)
- **Storage**: 32GB (sufficient for demos)
- **Region**: Auto-selected for lowest latency
- **Timeout**: 30 minutes (auto-suspend)

### Environment Variables
```bash
# Demo configuration
export DEMO_MODE=lightweight           # or 'full'
export AUTO_START=true                # Auto-start services
export H2O_MEM=2g                     # H2O memory limit
export STREAMLIT_SERVER_HEADLESS=true # Background mode
```

### Port Forwarding
- **8501**: Streamlit Dashboard (public)
- **54321**: H2O Cluster (public for advanced users)
- **8080**: Alternative port (if needed)

## 📈 Scaling for Enterprise Demos

### Multi-Client Demo Days
If presenting to multiple clients in one day:

1. **Morning Setup** (30 min)
   ```bash
   # Start once, use for multiple demos
   ./scripts/codespaces-demo.sh
   ```

2. **Between Demos** (5 min)
   ```bash
   # Light reset without full restart
   curl -X POST http://localhost:8501/_stcore/reset
   ```

3. **End of Day**
   ```bash
   ./scripts/stop-demo.sh
   ```

### Shared Demo Environment
For team presentations or workshops:
- Use 4-core Codespace for better performance
- Enable full demo mode
- Budget ~4-8 core hours for half-day events

## 🛟 Troubleshooting

### Common Issues

**Q: Dashboard not loading?**
```bash
# Check services
curl http://localhost:8501/_stcore/health
docker ps | grep h2o
```

**Q: H2O cluster not responding?**
```bash
# Restart H2O
docker restart h2o-demo
# Wait 30 seconds then check
curl http://localhost:54321
```

**Q: Out of Codespaces hours?**
- Upgrade to GitHub Pro ($4/month) for 180 core-hours
- Or use local Docker deployment for development

### Performance Optimization

**Slow startup?**
```bash
# Pre-pull Docker images (do once)
docker pull h2oai/h2o-open-source:latest
docker pull python:3.9-slim
```

**Memory issues?**
```bash
# Monitor usage
docker stats h2o-demo
free -h
```

## 💡 Best Practices

### Client Demo Checklist
- [ ] Test demo 1 day before client meeting
- [ ] Start Codespace 5 minutes before demo
- [ ] Have backup slides ready (PDF)
- [ ] Record demo for follow-up sharing
- [ ] Stop services immediately after demo

### Cost Management
- [ ] Set GitHub spending limit ($5-10/month safety)
- [ ] Monitor usage in GitHub Settings > Billing
- [ ] Use lightweight mode for short demos
- [ ] Schedule demos to minimize concurrent usage

### Professional Presentation
- [ ] Bookmark dashboard URL beforehand
- [ ] Prepare custom data upload (client's sample data)
- [ ] Practice demo flow (aim for 20-25 minutes)
- [ ] Have ROI calculator ready for their industry

---

**📞 Need Help?**
- Create GitHub Issue for technical problems
- Check GitHub Codespaces documentation
- Contact support for billing questions

*This deployment strategy optimizes for maximum client impact while minimizing infrastructure costs.*