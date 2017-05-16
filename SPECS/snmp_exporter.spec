%define debug_package %{nil}

%define _git_slug src/github.com/prometheus/snmp_exporter

Name:    snmp_exporter
Version: 0.3.0
Release: 2.vortex%{?dist}
Summary: SNMP Exporter for Prometheus
License: ASL 2.0
Vendor:  Vortex RPM
URL:     https://github.com/prometheus/snmp_exporter

Source1: %{name}.service
Source2: %{name}.default
Source3: %{name}.init

%{?el6:Requires(post): chkconfig}
%{?el6:Requires(preun): chkconfig, initscripts}
Requires(pre): shadow-utils
%{?el6:Requires: daemonize}
%{?el7:%{?systemd_requires}}
BuildRequires: golang, git

%description
A SNMP exporter for prometheus.

%prep
mkdir _build
export GOPATH=$(pwd)/_build
git clone https://github.com/prometheus/%{name} $GOPATH/%{_git_slug}
cd $GOPATH/%{_git_slug}
git checkout v%{version}

%build
export GOPATH=$(pwd)/_build
cd $GOPATH/%{_git_slug}
make format
make build

%install
export GOPATH=$(pwd)/_build
mkdir -vp %{buildroot}/var/lib/prometheus
%{?el6:mkdir -vp %{buildroot}/usr/sbin}
%{?el7:mkdir -vp %{buildroot}/usr/bin}
%{?el6:mkdir -vp %{buildroot}%{_initddir}}
%{?el7:mkdir -vp %{buildroot}/usr/lib/systemd/system}
mkdir -vp %{buildroot}/etc/default
mkdir -vp %{buildroot}/etc/prometheus
%{?el6:install -m 755 $GOPATH/%{_git_slug}/%{name} %{buildroot}/usr/sbin/%{name}}
%{?el7:install -m 755 $GOPATH/%{_git_slug}/%{name} %{buildroot}/usr/bin/%{name}}
%{?el6:install -m 755 %{SOURCE3} %{buildroot}%{_initddir}/%{name}}
%{?el7:install -m 755 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service}
install -m 644 %{SOURCE2} %{buildroot}/etc/default/%{name}
install -m 644 $GOPATH/%{_git_slug}/snmp.yml %{buildroot}/etc/prometheus/snmp.yml

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
%{?el6:/sbin/chkconfig --add %{name}}
%{?el7:%systemd_post %{name}.service}

%preun
%{?el6:
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
}
%{?el7:%systemd_preun %{name}.service}

%postun
%{?el6:
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} restart >/dev/null 2>&1
fi
}
%{?el7:%systemd_postun %{name}.service}

%files
%defattr(-,root,root,-)
%{?el6:/usr/sbin/%{name}}
%{?el7:/usr/bin/%{name}}
%{?el6:%{_initddir}/%{name}}
%{?el7:/usr/lib/systemd/system/%{name}.service}
%config(noreplace) /etc/default/%{name}
%config(noreplace) /etc/default/snmp.yml
%attr(755, prometheus, prometheus)/var/lib/prometheus
%doc _build/%{_git_slug}/CONTRIBUTING.md _build/%{_git_slug}/LICENSE _build/%{_git_slug}/NOTICE _build/%{_git_slug}/README.md _build/%{_git_slug}/MAINTAINERS.md

%changelog
* Wed May 17 2017 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.3.0-2.vortex
- Add missing snmp.yml
- Minor init/unit fixes

* Wed May 17 2017 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.3.0-1.vortex
- Initial packaging
