output "public_ip" {
  description = "Public IP address of the MicroShop server"
  value       = aws_instance.microshop_server.public_ip
}

output "public_dns" {
  description = "Public DNS of the MicroShop server"
  value       = aws_instance.microshop_server.public_dns
}

output "frontend_url" {
  description = "URL of the frontend application"
  value       = "http://${aws_instance.microshop_server.public_ip}"
}

output "grafana_url" {
  description = "URL of Grafana monitoring dashboard"
  value       = "http://${aws_instance.microshop_server.public_ip}:3000"
}

output "prometheus_url" {
  description = "URL of Prometheus"
  value       = "http://${aws_instance.microshop_server.public_ip}:9090"
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.microshop_server.public_ip}"
}
