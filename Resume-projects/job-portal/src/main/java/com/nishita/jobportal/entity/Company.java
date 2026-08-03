package com.nishita.jobportal.entity;

import jakarta.persistence.*;

@Entity @Table(name="companies")
public class Company {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @Column(nullable=false) private String name;
    private String website; private String location;
    @Column(length=2000) private String description;
    @ManyToOne(optional=false) @JoinColumn(name="recruiter_id") private UserAccount recruiter;
    public Long getId(){return id;} public String getName(){return name;} public void setName(String v){name=v;}
    public String getWebsite(){return website;} public void setWebsite(String v){website=v;}
    public String getLocation(){return location;} public void setLocation(String v){location=v;}
    public String getDescription(){return description;} public void setDescription(String v){description=v;}
    public UserAccount getRecruiter(){return recruiter;} public void setRecruiter(UserAccount v){recruiter=v;}
}
